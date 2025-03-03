from urllib.parse import quote_plus
import requests

def fetch_jira_issues(jira_url, jql, auth):
    encoded_jql = quote_plus(jql)
    url = f"{jira_url}/rest/api/3/search?jql={encoded_jql}"
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers, auth=auth)
    if response.status_code == 200:
        data = response.json()
        if data.get("total", 0) > 0:
            return data["issues"]
        return None
    raise Exception(f"Failed to fetch issues: {response.status_code}, Response: {response.text}")