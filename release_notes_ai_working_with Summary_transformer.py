import os
import requests
from transformers import pipeline
from urllib.parse import quote_plus
import json

# Initialize summarizer
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Fetch JIRA Issues
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

# Extract text from Atlassian Document Format (ADF)
def extract_adf_text(adf_content):

    if not isinstance(adf_content, dict) or "content" not in adf_content:
        return ""

    def parse_node(node):
        if isinstance(node, dict):
            node_type = node.get("type", "")
            if node_type == "text":
                return node.get("text", "")
            elif node_type in ["paragraph", "heading"]:
                return " ".join(parse_node(child) for child in node.get("content", []))
        elif isinstance(node, list):
            return " ".join(parse_node(item) for item in node)

        return ""

    return parse_node(adf_content).strip()

# Summarize all issues
def summarize_category(issues, category, version):
    if not issues:
        return f"No {category.lower()} items for this release."

    combined_text = []
    for issue in issues:
        summary = issue["fields"]["summary"]
        description_field = issue["fields"].get("description", "")

        if isinstance(description_field, dict) and description_field.get("type") == "doc":
            description = extract_adf_text(description_field)
        else:
            description = description_field or ""

        combined_text.append(f"{summary}: {description}")

    full_text = " ".join(combined_text)

    # 🛠 Dynamically adjust summary size
    input_length = len(full_text.split())
    max_length = min(300, max(100, int(input_length * 0.6)))  # Increase the output size
    min_length = max(80, int(max_length * 0.7))

    print(f"🔍 Summarizing {len(issues)} issues for category: {category} "
          f"(Input: {input_length} words → Max: {max_length}, Min: {min_length})")

    summarized_text = summarizer(
        full_text,
        max_length=max_length,
        min_length=min_length,
        do_sample=False,
        truncation=True  # Ensures input is not too large
    )

    return summarized_text[0]["summary_text"] if summarized_text else "Summarization failed."

# Generate Release Notes
def generate_release_notes(version, categories):
    release_notes = f"""# Release Notes - {version}

Hello there,

We are glad to inform you that the latest version **{version}** of **Go CI/CD** is out. Below are the Jira issues included in this release.

## **Summary**  
"""

    for category, issues in categories.items():
        if issues:
            summarized_text = summarize_category(issues, category, version)
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

    release_notes += ("\nA big shoutout to these amazing individuals who helped make this release a success! 🎉 "
                      "\nLooking forward to hearing your feedback."
                      "\n"
                      "\nThanks,\n"
                      "**Go CI/CD**")

    return release_notes

# Save Release Notes
def save_release_notes(release_notes, file_path):
    try:
        with open(file_path, "w") as f:
            f.write(release_notes)
        print(f"✅ Release Notes Saved to {file_path}")
    except Exception as e:
        print(f"❌ Error saving release notes: {str(e)}")

        fallback_path = "release_notes.md"
        with open(fallback_path, "w") as f:
            f.write(release_notes)
        print(f"✅ Release Notes Saved to fallback location: {fallback_path}")


def main():
    print("📢 Starting Release Notes Generation...")

    with open('../temp/config.json', 'r') as f:
        config = json.load(f)
    print("✅ Config file loaded.")

    jira_url = config['JIRA_URL']
    auth = (config['JIRA_USERNAME'], config['JIRA_PASSWORD'])
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
