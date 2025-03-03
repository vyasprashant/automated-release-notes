# Release Notes Accelerator (No UI)

This is the baseline version of the Release Notes Accelerator, a Python tool for generating release notes from Jira issues. It processes Jira data, summarizes issues using configurable methods (Hugging Face, OpenAI, Ollama), and outputs release notes to a Markdown file. This version does not include a user interface (UI) or advanced command-line options, relying instead on a `config.yaml` file for settings.

## Features
- **Core Logic**: Fetches Jira issues, categorizes them, and generates summaries.
- **Summarizers**: Supports Hugging Face, OpenAI, and Ollama for issue summarization.
- **Output**: Saves release notes as a Markdown file.
- **Config-Driven**: Uses a YAML configuration file for all settings.

## Prerequisites
- **Python 3.9**: Installed on your system.
- **Jira Access**: Valid Jira credentials (username and API token).
- **Dependencies**: Install required Python packages (see `requirements.txt`).

## Project Structure
```
arnr2/
├── README.md
├── cli.py             # Main script with core logic
├── config.yaml        # Configuration file (create manually)
├── requirements.txt   # Python dependencies
├── fetchers/
│   └── jira_fetcher.py
├── summarizers/
│   ├── huggingface_summarizer.py
│   ├── openai_summarizer.py
│   └── ollama_summarizer.py
├── formatters/
│   ├── markdown_formatter.py
│   ├── json_formatter.py
│   └── html_formatter.py
├── exporters/
│   └── file_exporter.py
└── output/            # Generated files (created at runtime)
```

## Setup

### 1. Clone the Repository
```
git clone <repository-url>
cd arnr2 
```
### 2. Install Dependencies
```
pip install -r requirements.txt
```
### 3. Configure
Create a config.yaml file in the project root with your settings. Example:
```
jira:
  url: "https://<project>.atlassian.net"
  username: "your-email@example.com"
  password: "your-jira-api-token"
version: "version"
summarizer:
  type: "ollama"  # Options: "huggingface", "openai", "ollama"
  openai_api_key: "your-openai-key"  # Required if type is "openai"
output:
  file_path: "output/release_notes.md"
```
- Replace placeholders with your actual Jira credentials and preferences.
- For Ollama, ensure it’s running locally or on a network-accessible server (update ollama_summarizer.py if needed).

## Usage
### Run the Script
```
python cli.py
```
- The script reads config.yaml, fetches Jira issues, generates summaries, and saves the release notes to the specified file (e.g., output/release_notes.md).

### Output
**File:** Saved to the path specified in config.yaml (e.g., output/release_notes.md) in Markdown format.

## Configuration Details
- **JIRA**:
    - url: Your Jira instance URL.
    - username: Your Jira username (typically an email).
    - password: Your Jira API token.
- Version: The release version to filter Jira issues (e.g., Test-release-0.1.0).
- Summarizer:
    - type: One of huggingface, openai, or ollama.
    - openai_api_key: Required for OpenAI summarizer.
- Output:
    - file_path: Path where the Markdown file will be saved.

## Troubleshooting
**Jira Errors**: Verify credentials and network access. Check logs for details:
```
python cli.py
```

####  Ollama Connection: If using Ollama, ensure it’s running:
```
docker run -d -p 11434:11434 ollama/ollama
```
Update summarizers/ollama_summarizer.py to use http://localhost:11434/api/generate if local.
- **Missing Dependencies**: Ensure all packages are installed:

```
pip install -r requirements.txt
```

## Development Notes
* Built with Python 3.9.
* Dependencies listed in requirements.txt.
* No UI or CLI options; relies on config.yaml for customization.

## Contributing
This is the baseline version. For UI or CLI enhancements, see other branches:

* ui: Streamlit UI version.
* cli-options: CLI with command-line arguments.
* all-in-one: Combined UI and CLI features.
  Submit issues or pull requests to enhance this version or suggest improvements!


---
## Summarized Execution Steps

#### Build
```
docker build -t release-notes-generator .
```
#### Run
```
docker run --rm \
   -v $(pwd)/config.yaml:/app/config.yaml \
   -v $(pwd)/output:/app/output \
   --network release-net \
   release-notes-generator python main.py --config /app/config.yaml --summarizer ollama
```
#### Run Ollama (if not already running)
```
docker network create release-net

docker run -d --name ollama --network release-net -p 11434:11434 ollama/ollama
```