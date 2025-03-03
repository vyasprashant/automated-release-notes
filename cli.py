import yaml
from fetchers.jira_fetcher import fetch_jira_issues
from summarizers.huggingface_summarizer import HuggingFaceSummarizer
from summarizers.openai_summarizer import OpenAISummarizer
from summarizers.ollama_summarizer import OllamaSummarizer
from formatters.markdown_formatter import format_markdown
from exporters.file_exporter import export_to_file

def categorize_issues(issues):
    categories = {}
    for issue in issues:
        issue_type = issue['fields']['issuetype']['name']
        if issue_type not in categories:
            categories[issue_type] = []
        categories[issue_type].append(issue)
    return categories

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

def generate_release_notes(config_file="config.yaml"):
    with open(config_file, 'r') as f:
        cfg = yaml.safe_load(f)

    jira_url = cfg['jira']['url']
    auth = (cfg['jira']['username'], cfg['jira']['password'])
    version = cfg['version']
    summarizer_type = cfg['summarizer']['type']

    jql = f"project = CICD AND fixVersion = \"{version}\" AND issuetype IN (\"Story\", \"New Functionality\", \"Improvement\", \"Task\", \"Bug\")"
    issues = fetch_jira_issues(jira_url, jql, auth) or fetch_jira_issues(jira_url, "project = CICD", auth)

    if not issues:
        print("No issues found.")
        return

    categories = categorize_issues(issues)
    summaries = {}

    if summarizer_type == "huggingface":
        summarizer = HuggingFaceSummarizer()
    elif summarizer_type == "openai":
        summarizer = OpenAISummarizer(cfg['summarizer']['openai_api_key'])
    elif summarizer_type == "ollama":
        summarizer = OllamaSummarizer()

    for category, issue_list in categories.items():
        combined_text = " ".join(f"{issue['fields']['summary']}: {extract_adf_text(issue['fields'].get('description', '')) or ''}" for issue in issue_list)
        if combined_text:
            summaries[category] = summarizer.summarize(combined_text, version_name=version) if summarizer_type == "ollama" else summarizer.summarize(combined_text)

    release_notes = format_markdown(version, categories, summaries, categories)
    export_to_file(release_notes, cfg['output']['file_path'])

if __name__ == "__main__":
    generate_release_notes()