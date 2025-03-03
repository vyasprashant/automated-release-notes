import click
import yaml
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

@click.command()
@click.option('--config', default='config.yaml', help='Path to config file')
@click.option('--summarizer', default='huggingface', help='Summarization engine: huggingface, openai, ollama')
@click.option('--format', default='markdown', help='Output format: markdown, html, json')
@click.option('--jql', default=None, help='Custom JQL query to override config')
@click.option('--output-type', type=click.Choice(['file', 'confluence']), default=None, help='Output destination: file or confluence')
def generate_release_notes(config, summarizer, format, jql, output_type):
    """Generate release notes from Jira issues with customizable summarization and output."""
    try:
        with open(config, 'r') as f:
            cfg = yaml.safe_load(f)
    except FileNotFoundError:
        raise click.ClickException(f"Config file '{config}' not found")
    except yaml.YAMLError as e:
        raise click.ClickException(f"Invalid YAML in config file: {str(e)}")

    # Validate config
    required_fields = ['jira', 'version', 'output']
    missing = [field for field in required_fields if field not in cfg]
    if missing:
        raise click.ClickException(f"Missing config fields: {missing}")
    if 'url' not in cfg['jira'] or 'username' not in cfg['jira'] or 'password' not in cfg['jira']:
        raise click.ClickException("Missing required fields in 'jira' config: url, username, password")

    jira_url = cfg['jira']['url']
    auth = (cfg['jira']['username'], cfg['jira']['password'])
    version = cfg['version']
    summarizer_type = summarizer

    # Define JQL queries
    default_project = "CICD"
    issue_types = "issuetype IN (\"Story\", \"New Functionality\", \"Improvement\", \"Task\", \"Bug\")"
    jql_with_version = f"project = {default_project} AND fixVersion = \"{version}\" AND {issue_types}"
    jql_without_version = f"project = {default_project} AND {issue_types}"

    # Use custom JQL from CLI or config if provided, otherwise default
    jql_to_use = jql if jql else cfg['jira'].get('jql', jql_with_version).format(version=version)

    # Fetch Jira issues with version
    try:
        print(f"Fetching issues with JQL: {jql_to_use}")
        issues = fetch_jira_issues(jira_url, jql_to_use, auth)
    except Exception as e:
        print(f"⚠️ Failed initial fetch: {str(e)}")

    # Fallback if no issues or fetch fails due to fixVersion
    if not issues:
        print(f"Falling back to broader query: {jql_without_version}")
        try:
            issues = fetch_jira_issues(jira_url, jql_without_version, auth)
        except Exception as e:
            raise click.ClickException(f"Failed to fetch fallback Jira issues: {str(e)}")

    if not issues:
        print("⚠️ No issues found with either query. Exiting...")
        return

    # Categorize issues
    categories = categorize_issues(issues)
    summaries = {}

    # Initialize summarizer
    try:
        if summarizer_type == "huggingface":
            summarizer = HuggingFaceSummarizer()
        elif summarizer_type == "openai":
            if 'summarizer' not in cfg or 'openai_api_key' not in cfg['summarizer']:
                raise click.ClickException("Missing 'openai_api_key' in config for OpenAI summarizer")
            summarizer = OpenAISummarizer(cfg['summarizer']['openai_api_key'])
        elif summarizer_type == "ollama":
            summarizer = OllamaSummarizer()
        else:
            raise click.ClickException(f"Unsupported summarizer: {summarizer_type}")
    except Exception as e:
        raise click.ClickException(f"Failed to initialize summarizer: {str(e)}")

    # Generate summaries
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

    # Generate release notes based on format
    formatters = {
        "markdown": format_markdown,
        "json": format_json,
        "html": format_html
    }
    if format not in formatters:
        raise click.ClickException(f"Unsupported format: {format}")
    release_notes = formatters[format](version, categories, summaries, categories)

    # Determine output type (CLI option overrides config)
    output_type = output_type if output_type else cfg['output'].get('type', 'file')
    if output_type == "file":
        if 'file_path' not in cfg['output']:
            raise click.ClickException("Missing 'file_path' in output config")
        file_extension = "md" if format == "markdown" else format
        file_path = f"{cfg['output']['file_path'].rsplit('.', 1)[0]}.{file_extension}"
        try:
            export_to_file(release_notes, file_path)
        except Exception as e:
            raise click.ClickException(f"Failed to export to file: {str(e)}")
    elif output_type == "confluence":
        markdown_notes = format_markdown(version, categories, summaries, categories)
        try:
            export_to_confluence(markdown_notes, cfg)
        except Exception as e:
            raise click.ClickException(f"Failed to export to Confluence: {str(e)}")
    else:
        raise click.ClickException(f"Unsupported output type: {output_type}")

if __name__ == "__main__":
    generate_release_notes()