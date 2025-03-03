def format_markdown(version, categories, summaries, issues):
    release_notes = f"""# Release Notes - {version}

Hello there,

We are glad to inform you that the latest version **{version}** of **Go CI/CD** is out. Below are the Jira issues included in this release.

## **Summary**  
"""
    for category, summary in summaries.items():
        release_notes += f"### **{category}s**\n{summary}\n\n"

    release_notes += "## **Detailed Issues List**\n\n"
    release_notes += "| Priority  | Key   | Summary | Status  |\n"
    release_notes += "|-----------|------|---------|---------|\n"
    for category, issue_list in issues.items():
        for issue in issue_list:
            priority = issue['fields']['priority']['name']
            key = issue['key']
            summary = issue['fields']['summary']
            status = issue['fields']['status']['name']
            release_notes += f"| {priority} | {key} | {summary} | {status} |\n"

    release_notes += ("\nA big shoutout to these amazing individuals who helped make this release a success! 🎉\n"
                      "Thanks,\n"
                      "**Go CI/CD**")
    return release_notes