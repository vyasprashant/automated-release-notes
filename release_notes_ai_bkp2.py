import os
import requests
import json

# Step 1: Fetch JIRA Issues
def fetch_jira_issues(jira_url, jql, auth):
    url = f"{jira_url}/rest/api/2/search"
    headers = {"Content-Type": "application/json"}
    payload = {"jql": jql, "maxResults": 1000}
    response = requests.get(url, headers=headers, auth=auth, params=payload)
    if response.status_code == 200:
        return response.json()['issues']
    else:
        raise Exception(f"Failed to fetch issues: {response.status_code}, Response: {response.text}")

# Step 2: Categorize Issues
def categorize_issues(issues):
    stories = []
    new_functionalities = []
    improvements = []
    tasks = []
    bugs = []

    for issue in issues:
        issue_type = issue['fields']['issuetype']['name'].lower()
        if issue_type == "story":
            stories.append(issue)
        elif issue_type == "new functionality":
            new_functionalities.append(issue)
        elif issue_type == "improvement":
            improvements.append(issue)
        elif issue_type == "task":
            tasks.append(issue)
        elif issue_type == "bug":
            bugs.append(issue)

    return stories, new_functionalities, improvements, tasks, bugs

# Step 3: Summarize Issues
def summarize_issues(issues):
    summaries = []
    for issue in issues:
        summary = issue['fields']['summary']
        summaries.append(summary)  # Use summary as is, can be enhanced with NLP if needed
    return summaries

# Step 4: Generate Release Notes
def generate_release_notes(version, stories, new_functionalities, improvements, tasks, bugs):
    release_notes = f"""
Hello there,

We are glad to inform you that the latest version {version} of Go CI/CD is out. Below is the list of Jira issues that were part of this upgrade.

# Summary

## Stories
The {version} focuses on {". ".join(stories) if stories else "No stories in this release"}.

## New Features/Functionality
The {version} introduces new features including {". ".join(new_functionalities) if new_functionalities else "No new functionalities in this release"}.

## Summary of Improvements
The {version} includes several improvements: {". ".join(improvements) if improvements else "No improvements in this release"}.

## Summary of Tasks
The {version} brings a multitude of enhancements and optimizations across our systems. Key highlights include {". ".join(tasks) if tasks else "No tasks in this release"}.

## Summary of Bugs
The {version} introduces several critical fixes to enhance operational efficiency. This release addresses {". ".join(bugs) if bugs else "No bugs in this release"}.

Project - Go CI/CD
Version - {version}
Planned Release Date - <RELEASE_DATE>

# Detailed List of Changes

## Stories
"""

    if stories:
        for story in stories:
            priority = story['fields']['priority']['name']
            key = story['key']
            summary = story['fields']['summary']
            status = story['fields']['status']['name']
            release_notes += f"- {priority} | {key} | {summary} | {status}\n"
    else:
        release_notes += "No stories in this release.\n"

    release_notes += "\n## New Features/Functionality\n"
    if new_functionalities:
        for func in new_functionalities:
            priority = func['fields']['priority']['name']
            key = func['key']
            summary = func['fields']['summary']
            status = func['fields']['status']['name']
            release_notes += f"- {priority} | {key} | {summary} | {status}\n"
    else:
        release_notes += "No new functionalities in this release.\n"

    release_notes += "\n## Improvements\n"
    if improvements:
        for improvement in improvements:
            priority = improvement['fields']['priority']['name']
            key = improvement['key']
            summary = improvement['fields']['summary']
            status = improvement['fields']['status']['name']
            release_notes += f"- {priority} | {key} | {summary} | {status}\n"
    else:
        release_notes += "No improvements in this release.\n"

    release_notes += "\n## Tasks\n"
    if tasks:
        for task in tasks:
            priority = task['fields']['priority']['name']
            key = task['key']
            summary = task['fields']['summary']
            status = task['fields']['status']['name']
            release_notes += f"- {priority} | {key} | {summary} | {status}\n"
    else:
        release_notes += "No tasks in this release.\n"

    release_notes += "\n## Bugs\n"
    if bugs:
        for bug in bugs:
            priority = bug['fields']['priority']['name']
            key = bug['key']
            summary = bug['fields']['summary']
            status = bug['fields']['status']['name']
            release_notes += f"- {priority} | {key} | {summary} | {status}\n"
    else:
        release_notes += "No bugs in this release.\n"

    return release_notes

# Step 5: Save Release Notes to a File
def save_release_notes(release_notes, file_path):
    with open(file_path, 'w') as f:
        f.write(release_notes)
    print(f"Release notes saved to {file_path}")

# Main Function
def main():
    # Load configuration
    with open('../temp/config.json', 'r') as f:
        config = json.load(f)

    # Step 1: Fetch JIRA Issues
    jira_url = config['JIRA_URL']
    version = "Test-release-0.1.0"
    jql = f'project = "Go CI/CD" AND fixVersion = "{version}"'
    auth = (config['JIRA_USERNAME'], config['JIRA_PASSWORD'])

    print(f"Fetching issues from {jira_url} with JQL: {jql}")
    issues = fetch_jira_issues(jira_url, jql, auth)
    print(f"Found {len(issues)} issues matching the query.")

    if len(issues) == 0:
        print("No issues found. Check your JQL query and permissions.")
        return

    # Step 2: Categorize Issues
    stories, new_functionalities, improvements, tasks, bugs = categorize_issues(issues)
    print(f"Found {len(stories)} stories, {len(new_functionalities)} new functionalities, " +
          f"{len(improvements)} improvements, {len(tasks)} tasks, and {len(bugs)} bugs.")

    # Print some details
    if len(issues) > 0:
        first_issue = issues[0]
        print(f"First issue: {first_issue['key']} - {first_issue['fields']['summary']}")
        print(f"Issue type: {first_issue['fields']['issuetype']['name']}")

    # Step 3: Summarize Issues
    summarized_stories = summarize_issues(stories)
    summarized_new_functionalities = summarize_issues(new_functionalities)
    summarized_improvements = summarize_issues(improvements)
    summarized_tasks = summarize_issues(tasks)
    summarized_bugs = summarize_issues(bugs)

    # Step 4: Generate Release Notes
    release_notes = generate_release_notes(
        version,
        summarized_stories,
        summarized_new_functionalities,
        summarized_improvements,
        summarized_tasks,
        summarized_bugs
    )
    print(release_notes)

    # Step 5: Save Release Notes to a File
    save_release_notes(release_notes, 'release_notes.md')

if __name__ == "__main__":
    main()