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

@click.command()
@click.option('--config', default='config.yaml', help='Path to config file')
@click.option('--jira-url', help='Jira instance URL')
@click.option('--jira-username', help='Jira username')
@click.option('--jira-token', help='Jira API token', hide_input=True)
@click.option('--version', help='Release version')
@click.option('--jql', help='Custom JQL query to override default')
@click.option('--summarizer', type=click.Choice(['huggingface', 'openai', 'ollama']), default='huggingface', help='Summarization engine')
@click.option('--openai-api-key', help='OpenAI API key (required for openai summarizer)', hide_input=True)
@click.option('--output-type', type=click.Choice(['file', 'confluence', 'both']), multiple=True, help='Output destination: file, confluence, or both')
@click.option('--file-path', help='Path for file output')
@click.option('--file-format', type=click.Choice(['markdown', 'json', 'html']), default='markdown', help='File output format')
@click.option('--confluence-url', help='Confluence instance URL')
@click.option('--confluence-username', help='Confluence username')
@click.option('--confluence-token', help='Confluence API token', hide_input=True)
@click.option('--space-key', help='Confluence space key')
@click.option('--page-title', help='Confluence page title')
@click.option('--parent-page-id', help='Confluence parent page ID (optional)')
def generate_release_notes(config, jira_url, jira_username, jira_token, version, jql, summarizer, openai_api_key,
                           output_type, file_path, file_format, confluence_url, confluence_username, confluence_token,
                           space_key, page_title, parent_page_id):
    """Generate release notes from Jira issues with customizable options."""
    # Load config file if it exists
    cfg = {}
    try:
        with open(config, 'r') as f:
            cfg = yaml.safe_load(f) or {}
    except FileNotFoundError:
        click.echo(f"Config file '{config}' not found. Using CLI options.")
    except yaml.YAMLError as e:
        raise click.ClickException(f"Invalid YAML in config file: {str(e)}")

    # Build config dictionary, prioritizing CLI options over config file
    cfg['jira'] = {
        'url': jira_url or cfg.get('jira', {}).get('url', 'https://uat-givaudan.atlassian.net'),
        'username': jira_username or cfg.get('jira', {}).get('username'),
        'password': jira_token or cfg.get('jira', {}).get('password')
    }
    cfg['version'] = version or cfg.get('version', 'Test-release-0.1.0')
    cfg['summarizer'] = {
        'type': summarizer or cfg.get('summarizer', {}).get('type', 'huggingface')
    }
    if summarizer == 'openai':
        cfg['summarizer']['openai_api_key'] = openai_api_key or cfg.get('summarizer', {}).get('openai_api_key')
    if jql:
        cfg['jira']['jql'] = jql

    # Validate Jira config
    if not all(k in cfg['jira'] for k in ['url', 'username', 'password']):
        raise click.ClickException("Missing required Jira fields: url, username, password")
    if summarizer == 'openai' and 'openai_api_key' not in cfg['summarizer']:
        raise click.ClickException("Missing OpenAI API key for 'openai' summarizer")

    # Output configuration
    output_types = list(output_type) if output_type else cfg.get('output', {}).get('type', ['file'])
    if not isinstance(output_types, list):
        output_types = [output_types]
    cfg['output'] = {
        'type': output_types,
        'file_path': file_path or cfg.get('output', {}).get('file_path', f"output/release_notes_{cfg['version']}.{file_format}"),
        'format': file_format or cfg.get('output', {}).get('format', 'markdown')
    }
    if 'confluence' in output_types:
        cfg['output']['confluence'] = {
            'url': confluence_url or cfg.get('output', {}).get('confluence', {}).get('url', 'https://uat-givaudan.atlassian.net/wiki'),
            'username': confluence_username or cfg.get('output', {}).get('confluence', {}).get('username'),
            'api_token': confluence_token or cfg.get('output', {}).get('confluence', {}).get('api_token'),
            'space_key': space_key or cfg.get('output', {}).get('confluence', {}).get('space_key', 'FP'),
            'page_title': page_title or cfg.get('output', {}).get('confluence', {}).get('page_title', f"Release Notes - {cfg['version']}"),
            'parent_page_id': parent_page_id or cfg.get('output', {}).get('confluence', {}).get('parent_page_id')
        }
        if not all(k in cfg['output']['confluence'] for k in ['url', 'username', 'api_token', 'space_key', 'page_title']):
            raise click.ClickException("Missing required Confluence fields: url, username, api_token, space_key, page_title")

    # Fetch Jira issues
    jira_url = cfg['jira']['url']
    auth = (cfg['jira']['username'], cfg['jira']['password'])
    version = cfg['version']
    summarizer_type = cfg['summarizer']['type']

    default_project = "CICD"
    issue_types = "issuetype IN (\"Story\", \"New Functionality\", \"Improvement\", \"Task\", \"Bug\")"
    jql_with_version = f"project = {default_project} AND fixVersion = \"{version}\" AND {issue_types}"
    jql_without_version = f"project = {default_project} AND {issue_types}"
    jql_to_use = cfg['jira'].get('jql', jql_with_version)

    try:
        click.echo(f"Fetching issues with JQL: {jql_to_use}")
        issues = fetch_jira_issues(jira_url, jql_to_use, auth)
    except Exception as e:
        click.echo(f"⚠️ Failed initial fetch: {str(e)}")
        issues = None

    if not issues:
        click.echo(f"Falling back to broader query: {jql_without_version}")
        try:
            issues = fetch_jira_issues(jira_url, jql_without_version, auth)
        except Exception as e:
            raise click.ClickException(f"Failed to fetch fallback Jira issues: {str(e)}")

    if not issues:
        click.echo("⚠️ No issues found with either query. Exiting...")
        return

    # Categorize issues
    categories = categorize_issues(issues)
    summaries = {}

    # Initialize summarizer
    try:
        if summarizer_type == "huggingface":
            summarizer = HuggingFaceSummarizer()
        elif summarizer_type == "openai":
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
                click.echo(f"⚠️ Failed to summarize '{category}': {str(e)}")
                summaries[category] = "Summary unavailable"

    # Generate release notes based on format
    formatters = {
        "markdown": format_markdown,
        "json": format_json,
        "html": format_html
    }
    if cfg['output']['format'] not in formatters:
        raise click.ClickException(f"Unsupported format: {cfg['output']['format']}")
    release_notes = formatters[cfg['output']['format']](version, categories, summaries, categories)
    markdown_notes = format_markdown(version, categories, summaries, categories)

    # Export based on output types
    if 'file' in cfg['output']['type']:
        try:
            export_to_file(release_notes, cfg['output']['file_path'])
            click.echo(f"✅ File saved to: {cfg['output']['file_path']}")
        except Exception as e:
            raise click.ClickException(f"Failed to export to file: {str(e)}")
    if 'confluence' in cfg['output']['type']:
        try:
            export_to_confluence(markdown_notes, cfg)
            click.echo("✅ Published to Confluence")
        except Exception as e:
            raise click.ClickException(f"Failed to export to Confluence: {str(e)}")

if __name__ == "__main__":
    generate_release_notes()