import argparse
import sys
from fetchers.jira_fetcher import fetch_jira_issues
from summarizers.huggingface_summarizer import HuggingFaceSummarizer
from summarizers.openai_summarizer import OpenAISummarizer
from summarizers.ollama_summarizer import OllamaSummarizer
from formatters.markdown_formatter import format_markdown
from formatters.json_formatter import format_json
from formatters.html_formatter import format_html
from exporters.file_exporter import export_to_file
from exporters.confluence_exporter import export_to_confluence

def categorize_issues(issues):
    """Categorize Jira issues by type."""
    categories = {}
    for issue in issues:
        issue_type = issue['fields']['issuetype']['name']
        if issue_type not in categories:
            categories[issue_type] = []
        categories[issue_type].append(issue)
    return categories

def extract_adf_text(adf_content):
    """Extract text from Jira ADF content."""
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

def generate_release_notes(cfg):
    if "jira" not in cfg or not all(k in cfg["jira"] for k in ["url", "username", "password"]):
        raise Exception("Missing required 'jira' config fields: url, username, password")
    jira_url = cfg["jira"]["url"]
    auth = (cfg["jira"]["username"], cfg["jira"]["password"])

    if "version" not in cfg:
        raise Exception("Missing 'version' in config")
    version = cfg["version"]

    if "summarizer" not in cfg or "type" not in cfg["summarizer"]:
        raise Exception("Missing 'summarizer' or 'type' in config")
    summarizer_type = cfg["summarizer"]["type"]

    if "output" not in cfg:
        raise Exception("Missing 'output' in config")
    output_config = cfg["output"]
    format = output_config.get("format", "markdown")

    default_project = "CICD"
    issue_types = "issuetype IN (\"Story\", \"New Functionality\", \"Improvement\", \"Task\", \"Bug\")"
    jql_with_version = f"project = {default_project} AND fixVersion = \"{version}\" AND {issue_types}"
    jql_without_version = f"project = {default_project} AND {issue_types}"
    jql_to_use = cfg["jira"].get("jql", jql_with_version)

    try:
        print(f"Fetching issues with JQL: {jql_to_use}")
        issues = fetch_jira_issues(jira_url, jql_to_use, auth)
    except Exception as e:
        print(f"⚠️ Failed initial fetch: {str(e)}")
        issues = None

    if not issues:
        print(f"Falling back to broader query: {jql_without_version}")
        try:
            issues = fetch_jira_issues(jira_url, jql_without_version, auth)
        except Exception as e:
            raise Exception(f"Failed to fetch fallback Jira issues: {str(e)}")

    if not issues:
        print("⚠️ No issues found with either query. Exiting...")
        return

    categories = categorize_issues(issues)
    summaries = {}

    try:
        if summarizer_type == "huggingface":
            summarizer = HuggingFaceSummarizer()
        elif summarizer_type == "openai":
            if "openai_api_key" not in cfg["summarizer"]:
                raise Exception("Missing 'openai_api_key' for OpenAI summarizer")
            summarizer = OpenAISummarizer(cfg["summarizer"]["openai_api_key"])
        elif summarizer_type == "ollama":
            summarizer = OllamaSummarizer()
        else:
            raise Exception(f"Unsupported summarizer: {summarizer_type}")
    except Exception as e:
        raise Exception(f"Failed to initialize summarizer: {str(e)}")

    for category, issue_list in categories.items():
        combined_text = []
        for issue in issue_list:
            summary = issue["fields"]["summary"]
            desc = issue["fields"].get("description", "")
            desc = extract_adf_text(desc) if isinstance(desc, dict) else desc or ""
            combined_text.append(f"{summary}: {desc}")
        full_text = " ".join(combined_text)
        if full_text:
            try:
                if summarizer_type == "ollama":
                    summaries[category] = summarizer.summarize(full_text, version_name=version)
                elif summarizer_type == "openai":
                    summaries[category] = summarizer.summarize(full_text, max_words=200)
                elif summarizer_type == "huggingface":
                    summaries[category] = summarizer.summarize(full_text)
            except Exception as e:
                print(f"⚠️ Failed to summarize '{category}': {str(e)}")
                summaries[category] = "Summary unavailable"

    formatters = {
        "markdown": format_markdown,
        "json": format_json,
        "html": format_html
    }
    if format not in formatters:
        raise Exception(f"Unsupported format: {format}")
    release_notes = formatters[format](version, categories, summaries, categories)
    markdown_notes = format_markdown(version, categories, summaries, categories)

    output_types = output_config.get("type", [])
    if "file" in output_types:
        if "file_path" not in output_config:
            raise Exception("Missing 'file_path' in output config for file output")
        file_path = output_config["file_path"]
        try:
            export_to_file(release_notes, file_path)
            print(f"✅ File saved to: {file_path}")
        except Exception as e:
            raise Exception(f"Failed to export to file: {str(e)}")

    if "confluence" in output_types:
        try:
            export_to_confluence(markdown_notes, cfg)
            print("✅ Published to Confluence")
        except Exception as e:
            raise Exception(f"Failed to export to Confluence: {str(e)}")

def run_cli():
    """Run the command-line interface."""
    parser = argparse.ArgumentParser(description="Generate release notes from Jira issues.")
    parser.add_argument("--jira-url", default="https://uat-givaudan.atlassian.net", help="Jira URL")
    parser.add_argument("--jira-username", help="Jira username")
    parser.add_argument("--jira-token", help="Jira API token")
    parser.add_argument("--version", default="Test-release-0.1.0", help="Release version")
    parser.add_argument("--jql", help="Custom JQL query")
    parser.add_argument("--summarizer", choices=["huggingface", "openai", "ollama"], default="huggingface", help="Summarizer type")
    parser.add_argument("--openai-api-key", help="OpenAI API key (required for openai summarizer)")
    parser.add_argument("--output", nargs="+", choices=["file", "confluence"], default=["file"], help="Output types (space-separated)")
    parser.add_argument("--file-path", default="output/release_notes.md", help="File path for file output")
    parser.add_argument("--file-format", choices=["markdown", "json", "html"], default="markdown", help="File format")
    parser.add_argument("--confluence-url", default="https://uat-givaudan.atlassian.net/wiki", help="Confluence URL")
    parser.add_argument("--confluence-username", help="Confluence username")
    parser.add_argument("--confluence-token", help="Confluence API token")
    parser.add_argument("--space-key", default="FP", help="Confluence space key")
    parser.add_argument("--page-title", default="Release Notes - {version}", help="Confluence page title")
    parser.add_argument("--parent-page-id", help="Confluence parent page ID")

    args = parser.parse_args()

    # Prompt for missing required fields
    jira_username = args.jira_username or input("Jira Username: ")
    jira_token = args.jira_token or input("Jira API Token: ")
    if "confluence" in args.output:
        confluence_username = args.confluence_username or input("Confluence Username: ")
        confluence_token = args.confluence_token or input("Confluence API Token: ")

    cfg = {
        "jira": {
            "url": args.jira_url,
            "username": jira_username,
            "password": jira_token,
        },
        "version": args.version,
        "summarizer": {
            "type": args.summarizer
        },
        "output": {
            "type": args.output
        }
    }
    if args.jql:
        cfg["jira"]["jql"] = args.jql
    if args.summarizer == "openai":
        openai_api_key = args.openai_api_key or input("OpenAI API Key: ")
        cfg["summarizer"]["openai_api_key"] = openai_api_key
    if "file" in args.output:
        cfg["output"]["file_path"] = args.file_path
        cfg["output"]["format"] = args.file_format
    if "confluence" in args.output:
        cfg["output"]["confluence"] = {
            "url": args.confluence_url,
            "username": confluence_username,
            "api_token": confluence_token,
            "space_key": args.space_key,
            "page_title": args.page_title.format(version=args.version),
            "parent_page_id": args.parent_page_id
        }

    try:
        generate_release_notes(cfg)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_cli()