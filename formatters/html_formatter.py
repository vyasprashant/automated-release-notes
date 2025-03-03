def format_html(version, categories, summaries, issues):
    html = f"""<!DOCTYPE html>
<html>
<head><title>Release Notes - {version}</title></head>
<body>
    <h1>Release Notes - {version}</h1>
    <p>Hello there,</p>
    <p>We are glad to inform you that the latest version <b>{version}</b> of <b>Go CI/CD</b> is out.</p>
    <h2>Summary</h2>
"""
    for category, summary in summaries.items():
        html += f"<h3>{category}s</h3><p>{summary}</p>"
    html += "<h2>Detailed Issues List</h2><table border='1'><tr><th>Priority</th><th>Key</th><th>Summary</th><th>Status</th></tr>"
    for category, issue_list in issues.items():
        for issue in issue_list:
            html += f"<tr><td>{issue['fields']['priority']['name']}</td><td>{issue['key']}</td><td>{issue['fields']['summary']}</td><td>{issue['fields']['status']['name']}</td></tr>"
    html += "</table><p>A big shoutout to these amazing individuals who helped make this release a success! 🎉</p><p>Thanks,<br><b>Go CI/CD</b></p></body></html>"
    return html