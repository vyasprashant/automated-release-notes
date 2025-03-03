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

def prompt_for_output_types():
    """Prompt user to select multiple output types."""
    output_options = {'1': 'confluence', '2': 'file'}
    click.echo("Select output types (enter numbers separated by spaces, e.g., '1 2'):")
    click.echo("1. Confluence")
    click.echo("2. File")
    while True:
        selection = click.prompt("Your choices", default="1").strip().split()
        selected = [output_options.get(s) for s in selection if s in output_options]
        if selected:
            return selected
        click.echo("Invalid selection. Please choose valid numbers (e.g., '1', '1 2').")

def prompt_for_confluence_config(cfg):
    """Prompt for Confluence details if not in config."""
    confluence_cfg = cfg.get('output', {}).get('confluence', {})
    return {
        'url': click.prompt("Confluence URL", default=confluence_cfg.get('url', "https://uat-givaudan.atlassian.net/wiki")),
        'username': click.prompt("Confluence Username", default=confluence_cfg.get('username', "")),
        'api_token': click.prompt("Confluence API Token", default=confluence_cfg.get('api_token', ""), hide_input=True),
        'space_key': click.prompt("Space Key", default=confluence_cfg.get('space_key', "FP")),
        'page_title': click.prompt("Page Title", default=confluence_cfg.get('page_title', "Release Notes - {version}")),
        'parent_page_id': click.prompt("Parent Page ID (optional)", default=confluence_cfg.get('parent_page_id', ""), show_default=False) or None
    }

@click.command()
@click.option('--config', default=None, help='Path to config file (optional)')
@click.option('--jql', default=None, help='Custom JQL query to override default')
def generate_release_notes(config, jql):
    """Interactively generate release notes from Jira issues."""
    # Load config if provided, otherwise start with empty dict
    cfg = {}
    if config:
        try:
            with open(config, 'r') as f:
                cfg = yaml.safe_load(f) or {}
        except FileNotFoundError:
            click.echo(f"Config file '{config}' not found. Proceeding with interactive prompts.")
        except yaml.YAMLError as e:
            raise click.ClickException(f"Invalid YAML in config file: {str(e)}")

    # Jira configuration
    jira_cfg = cfg.get('jira', {})
    jira_url = click.prompt("Jira URL", default=jira_cfg.get('url', "https://uat-givaudan.atlassian.net"))
    jira_username = click.prompt("Jira Username", default=jira_cfg.get('username', ""))
    jira_password = click.prompt("Jira API Token", default=jira_cfg.get('password', ""), hide_input=True)
    auth = (jira_username, jira_password)
    version = click.prompt("Release Version", default=cfg.get('version', "Test-release-0.1.0"))

    # Summarizer selection
    summarizer_options = {'1': 'huggingface', '2': 'openai', '3': 'ollama'}
    click.echo("Select a summarizer:")
    click.echo("1. Hugging Face")
    click.echo("2. OpenAI")
    click.echo("3. Ollama")
    while True:
        summarizer_choice = click.prompt("Your choice (1-3)", default="1")
        summarizer_type = summarizer_options.get(summarizer_choice)
        if summarizer_type:
            break
        click.echo("Invalid choice. Please enter 1, 2, or 3.")

    # Additional summarizer config if needed
    summarizer_cfg = cfg.get('summarizer', {})
    if summarizer_type == "openai":
        openai_api_key = click.prompt("OpenAI API Key", default=summarizer_cfg.get('openai_api_key', ""), hide_input=True)
        if not openai_api_key:
            raise click.ClickException("OpenAI API key is required for OpenAI summarizer")

    # Output configuration
    output_types = prompt_for_output_types()
    output_cfg = cfg.get('output', {})
    file_path = None
    confluence_cfg = None
    if 'file' in output_types:
        file_format = click.prompt("File output format", type=click.Choice(['markdown', 'json', 'html']), default='markdown')
        file_path = click.prompt("File path", default=output_cfg.get('file_path', f"output/release_notes_{version}.{file_format}"))
    if 'confluence' in output_types:
        confluence_cfg = prompt_for_confluence_config(cfg)

    # JQL setup
    default_project = "CICD"
    issue_types = "issuetype IN (\"Story\", \"New Functionality\", \"Improvement\", \"Task\", \"Bug\")"
    jql_with_version = f"project = {default_project} AND fixVersion = \"{version}\" AND {issue_types}"
    jql_without_version = f"project = {default_project} AND {issue_types}"
    jql_to_use = jql if jql else cfg.get('jira', {}).get('jql', jql_with_version).format(version=version)

    # Fetch Jira issues
    try:
        print(f"Fetching issues with JQL: {jql_to_use}")
        issues = fetch_jira_issues(jira_url, jql_to_use, auth)
    except Exception as e:
        print(f"⚠️ Failed initial fetch: {str(e)}")

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
            summarizer = OpenAISummarizer(openai_api_key)
        elif summarizer_type == "ollama":
            summarizer = OllamaSummarizer()
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

    # Formatters
    formatters = {
        "markdown": format_markdown,
        "json": format_json,
        "html": format_html
    }

    # Export based on selected output types
    if 'confluence' in output_types:
        markdown_notes = format_markdown(version, categories, summaries, categories)
        try:
            export_to_confluence(markdown_notes, {'output': {'confluence': confluence_cfg}, 'version': version})
        except Exception as e:
            raise click.ClickException(f"Failed to export to Confluence: {str(e)}")

    if 'file' in output_types:
        release_notes = formatters[file_format](version, categories, summaries, categories)
        try:
            export_to_file(release_notes, file_path)
        except Exception as e:
            raise click.ClickException(f"Failed to export to file: {str(e)}")

if __name__ == "__main__":
    generate_release_notes()