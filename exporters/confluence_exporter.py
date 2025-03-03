import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import quote_plus
import re

def markdown_to_storage(markdown_content):
    """Convert Markdown to Confluence Storage Format with improved formatting."""
    lines = markdown_content.split("\n")
    storage_lines = []
    in_table = False
    in_list = False

    def process_text(text):
        """Handle inline Markdown like bold."""
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)  # Bold
        return text

    for line in lines:
        line = line.strip()

        # Headings
        if line.startswith("# "):
            if in_table:
                storage_lines.append("</table>")
                in_table = False
            if in_list:
                storage_lines.append("</ul>")
                in_list = False
            storage_lines.append(f"<h1>{process_text(line[2:].strip())}</h1>")
        elif line.startswith("## "):
            if in_table:
                storage_lines.append("</table>")
                in_table = False
            if in_list:
                storage_lines.append("</ul>")
                in_list = False
            storage_lines.append(f"<h2>{process_text(line[3:].strip())}</h2>")
        elif line.startswith("### "):
            if in_table:
                storage_lines.append("</table>")
                in_table = False
            if in_list:
                storage_lines.append("</ul>")
                in_list = False
            storage_lines.append(f"<h3>{process_text(line[4:].strip())}</h3>")

        # Table start
        elif line.startswith("|") and not in_table and not in_list:
            in_table = True
            storage_lines.append('<table><colgroup><col style="width:120px"/><col style="width:80px"/><col style="width:400px"/><col style="width:100px"/></colgroup>')
            headers = [h.strip() for h in line.split("|")[1:-1]]
            storage_lines.append("<tr>")
            for header in headers:
                storage_lines.append(f"<th>{process_text(header)}</th>")
            storage_lines.append("</tr>")

        # Table separator
        elif in_table and re.match(r"^\|[-:\s]+\|", line):
            continue

        # Table row
        elif in_table and line.startswith("|"):
            cells = [c.strip() for c in line.split("|")[1:-1]]
            storage_lines.append("<tr>")
            for cell in cells:
                storage_lines.append(f"<td>{process_text(cell)}</td>")
            storage_lines.append("</tr>")

        # List item
        elif line.startswith("* "):
            if in_table:
                storage_lines.append("</table>")
                in_table = False
            if not in_list:
                storage_lines.append("<ul>")
                in_list = True
            storage_lines.append(f"<li>{process_text(line[2:].strip())}</li>")

        # End of table or list
        elif (in_table or in_list) and not line.startswith("|") and not line.startswith("* "):
            if in_table:
                storage_lines.append("</table>")
                in_table = False
            if in_list:
                storage_lines.append("</ul>")
                in_list = False
            if line:
                storage_lines.append(f"<p>{process_text(line)}</p>")

        # Regular paragraph
        elif line and not in_table and not in_list:
            storage_lines.append(f"<p>{process_text(line)}</p>")

    # Close any open tags
    if in_table:
        storage_lines.append("</table>")
    if in_list:
        storage_lines.append("</ul>")

    return "".join(storage_lines)

def check_existing_page(url, title, space_key, auth):
    check_url = f"{url}/rest/api/content?title={quote_plus(title)}&spaceKey={space_key}"
    response = requests.get(check_url, auth=auth)
    if response.status_code == 200 and response.json()["results"]:
        return response.json()["results"][0]["id"]
    return None

def export_to_confluence(content, cfg):
    confluence_cfg = cfg['output']['confluence']
    required_fields = ['url', 'username', 'api_token', 'space_key', 'page_title']
    missing = [field for field in required_fields if field not in confluence_cfg]
    if missing:
        raise ValueError(f"Missing Confluence config fields: {missing}")

    url = f"{confluence_cfg['url']}/rest/api/content"
    auth = HTTPBasicAuth(confluence_cfg['username'], confluence_cfg['api_token'])
    headers = {"Content-Type": "application/json"}
    title = confluence_cfg['page_title'].format(version=cfg['version'])
    storage_content = markdown_to_storage(content)

    existing_page_id = check_existing_page(confluence_cfg['url'], title, confluence_cfg['space_key'], auth)
    payload = {
        "type": "page",
        "title": title,
        "space": {"key": confluence_cfg['space_key']},
        "body": {
            "storage": {
                "value": storage_content,
                "representation": "storage"
            }
        }
    }
    if "parent_page_id" in confluence_cfg:
        payload["ancestors"] = [{"id": confluence_cfg["parent_page_id"]}]

    try:
        if existing_page_id:
            update_url = f"{url}/{existing_page_id}"
            payload["version"] = {"number": int(requests.get(update_url, auth=auth).json()["version"]["number"]) + 1}
            response = requests.put(update_url, json=payload, headers=headers, auth=auth)
        else:
            response = requests.post(url, json=payload, headers=headers, auth=auth)
        response.raise_for_status()
        page_id = response.json()["id"]
        print(f"✅ Published to Confluence: {confluence_cfg['url']}/pages/viewpage.action?pageId={page_id}")
        return page_id
    except requests.RequestException as e:
        raise Exception(f"Failed to publish to Confluence: {str(e)} - {response.text if 'response' in locals() else 'No response'}")