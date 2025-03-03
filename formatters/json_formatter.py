import json

def format_json(version, categories, summaries, issues):
    data = {
        "version": version,
        "summary": summaries,
        "issues": {category: [{"key": issue["key"], "summary": issue["fields"]["summary"],
                               "priority": issue["fields"]["priority"]["name"], "status": issue["fields"]["status"]["name"]}
                              for issue in issue_list] for category, issue_list in issues.items()}
    }
    return json.dumps(data, indent=2)