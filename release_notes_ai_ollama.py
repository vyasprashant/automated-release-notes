import os
import requests
import json
from urllib.parse import quote_plus

# Summarization function
def summarize_with_ollama(text):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "mistral",  # Change model based on your local Ollama setup
        "prompt": f"Summarize the following text:\n\n{text}",
        "stream": False
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json().get("response", "Summarization failed")
    else:
        return f"Error: {response.status_code}, {response.text}"

# Fetch JIRA Issues
def fetch_jira_issues(jira_url, jql, auth):
    encoded_jql = quote_plus(jql)
    url = f"{jira_url}/rest/api/3/search?jql={encoded_jql}"
    headers = {"Content-Type": "application/json"}

    response = requests.get(url, headers=headers, auth=auth)
    if response.status_code == 200:
        data = response.json()
        return data.get("issues", [])
    else:
        raise Exception(f"Failed to fetch issues: {response.status_code}, {response.text}")

# Categorize Issues
def categorize_issues(issues):
    categories = {"Story": [], "New Functionality": [], "Improvement": [], "Task": [], "Bug": []}
    for issue in issues:
        issue_type = issue['fields']['issuetype']['name']
        if issue_type in categories:
            categories[issue_type].append(issue)
    return categories

# Summarize Issues Using Ollama
def summarize_category(issues, category):
    if not issues:
        return f"No {category.lower()} items for this release."

    combined_text = ". ".join([
        issue['fields']['summary'] + " " + str(issue['fields'].get('description', ''))
        for issue in issues
    ])

    return summarize_with_ollama(combined_text)

# Generate Release Notes
def generate_release_notes(version, categories):
    release_notes = f"# Release Notes - {version}\n\n"
    release_notes += "## **Summary**\n\n"

    for category, issues in categories.items():
        if issues:
            summarized_text = summarize_category(issues, category)
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
    auth = (config['JIRA_USERNAME'], config['JIRA_PASSWORD'])
    version = config.get('VERSION', 'Test-release-0.1.0')

    jql = f'project = CICD AND fixVersion = "{version}" AND issuetype IN ("Story", "New Functionality", "Improvement", "Task", "Bug")'
    issues = fetch_jira_issues(jira_url, jql, auth)

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
