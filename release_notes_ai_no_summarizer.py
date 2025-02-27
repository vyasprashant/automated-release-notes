import os
import requests
from transformers import pipeline
from urllib.parse import quote_plus
import json

# Initialize summarizer
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Fetch JIRA Issues with fallback
def fetch_jira_issues(jira_url, jql, auth):
    encoded_jql = quote_plus(jql)
    url = f"{jira_url}/rest/api/3/search?jql={encoded_jql}"
    headers = {"Content-Type": "application/json"}

    response = requests.get(url, headers=headers, auth=auth)
    if response.status_code == 200:
        data = response.json()
        if data.get("total", 0) > 0:
            return data["issues"]
        else:
            print("⚠️ No issues found with fixVersion. Retrying without fixVersion...")
            return None
    else:
        raise Exception(f"Failed to fetch issues: {response.status_code}, Response: {response.text}")

# Categorize issues
def categorize_issues(issues):
    categories = {"Story": [], "New Functionality": [], "Improvement": [], "Task": [], "Bug": []}
    for issue in issues:
        issue_type = issue['fields']['issuetype']['name']
        if issue_type in categories:
            categories[issue_type].append(issue)
    return categories

# Summarize all issues in a category together
def summarize_category(issues, category):
    if not issues:
        return f"No {category.lower()} items for this release."

    combined_text = ". ".join([
        issue['fields']['summary'] + " " + str(issue['fields'].get('description', ''))
        for issue in issues
    ])

    # Limit input size (BART models usually have a max token limit of 1024)
    max_input_tokens = 500  # Adjust based on model limits
    words = combined_text.split()
    if len(words) > max_input_tokens:
        combined_text = " ".join(words[:max_input_tokens])  # Trim excess words

    input_length = len(combined_text.split())
    max_length = min(50, int(input_length * 0.8))  # Dynamic max length

    # Ensure max_length is reasonable
    if input_length < 10:
        max_length = 5
    elif input_length < 20:
        max_length = 10

    try:
        summarized_text = summarizer(
            combined_text,
            max_length=max_length,
            min_length=int(max_length * 0.5),
            do_sample=False
        )[0]['summary_text']
    except Exception as e:
        print(f"⚠️ Summarization error: {e}")
        summarized_text = f"Summary generation failed for {category.lower()}."

    return summarized_text



# Generate Release Notes
def generate_release_notes(version, categories):
    release_notes = f"""# Release Notes - {version}

Hello there,

We are glad to inform you that the latest version **{version}** of **Go CI/CD** is out. Below are the Jira issues included in this release.

## **Summary**  
"""

    for category, issues in categories.items():
        if issues:
            summarized_text = summarize_category(issues, category)
            if summarized_text:
                release_notes += f"### **{category}s**\n{summarized_text}\n\n"

    release_notes += "## **Detailed Issues List**\n\n"
    release_notes += "| Priority  | Key   | Summary | Status  |\n"
    release_notes += "|-----------|------|---------|---------|\n"

    for category, issues in categories.items():
        for issue in issues:
            priority = issue['fields']['priority']['name']
            key = issue['key']
            summary = issue['fields']['summary']
            status = issue['fields']['status']['name']
            release_notes += f"| {priority} | {key} | {summary} | {status} |\n"

    return release_notes

# Save Release Notes
def save_release_notes(release_notes, file_path):
    try:
        with open(file_path, "w") as f:
            f.write(release_notes)
        print(f"✅ Release Notes Saved to {file_path}")
    except Exception as e:
        print(f"❌ Error saving release notes: {str(e)}")
        # Fallback to current directory if output directory is not accessible
        fallback_path = "release_notes.md"
        with open(fallback_path, "w") as f:
            f.write(release_notes)
        print(f"✅ Release Notes Saved to fallback location: {fallback_path}")

# Main Function
def main():
    print("📢 Starting Release Notes Generation...")

    with open('../temp/config.json', 'r') as f:
        config = json.load(f)
    print("✅ Config file loaded.")

    jira_url = config['JIRA_URL']
    auth = (config['JIRA_USERNAME'], config['JIRA_PASSWORD'])  # Use API token as password
    version = config.get('VERSION', 'Test-release-0.1.0')

    jql_with_fixversion = f"""
    project = CICD 
    AND fixVersion = "{version}" 
    AND issuetype IN ("Story", "New Functionality", "Improvement", "Task", "Bug")
    """

    issues = fetch_jira_issues(jira_url, jql_with_fixversion, auth)

    if issues is None:
        jql_without_fixversion = """
        project = CICD 
        AND issuetype IN ("Story", "New Functionality", "Improvement", "Task", "Bug")
        """
        issues = fetch_jira_issues(jira_url, jql_without_fixversion, auth)

    if not issues:
        print("⚠️ No issues found. Exiting...")
        return

    categories = categorize_issues(issues)
    print(f"📌 Categorized Issues: { {key: len(value) for key, value in categories.items()} }")

    release_notes = generate_release_notes(version, categories)
    output_path = "/app/output/release_notes.md" if os.getenv("DOCKER_ENV") else "release_notes.md"
    save_release_notes(release_notes, output_path)

    print("✅ Release Notes Generation Completed!")

if __name__ == "__main__":
    main()