# Release Notes Accelerator

This project is a Dockerized tool for generating release notes from Jira issues, offering both a web-based UI (via Streamlit) and a command-line interface (CLI). It supports multiple summarization methods (Hugging Face, OpenAI, Ollama) and output options (Markdown file, Confluence, or both).

## Features
- **Dual Interface**: Choose between a user-friendly Streamlit UI or a flexible CLI.
- **Summarizers**: Supports Hugging Face, OpenAI, and Ollama for summarizing Jira issues.
- **Output Options**: Generate release notes as a Markdown file, publish to Confluence, or both.
- **Dockerized**: Runs seamlessly in Docker containers, including Ollama support.

## Prerequisites
- **Docker**: Installed and running on your system.
- **Jira Access**: Valid Jira credentials (username and API token).
- **Confluence Access** (optional): Valid Confluence credentials for publishing.

## Project Structure
```
arnr2/
├── Dockerfile
├── README.md
├── cli.py             # Core logic and CLI interface
├── entry.py           # Entry point to choose UI or CLI
├── ui.py              # Streamlit UI
├── requirements.txt   # Python dependencies
├── .streamlit/
│   └── config.toml    # Streamlit configuration
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
│   ├── file_exporter.py
│   └── confluence_exporter.py
└── output/            # Generated files (created/mounted)
```

## Setup

### 1. Clone the Repository
```
git clone <repository-url>
cd arnr2 
```
### 2. Build the Docker Image
```
docker build -t release-notes-app .
```
### 3. Run Ollama (Optional)
If using the Ollama summarizer:
```
docker network create release-net
docker run -d --name ollama --network release-net -p 11434:11434 ollama/ollama
```

## Usage
### UI Mode (Streamlit)
Run the web interface:
```
docker run -p 8501:8501 --network release-net -v $(pwd)/output:/app/output release-notes-app
```
- Access the UI at http://localhost:8501.
- Fill in:
  - Jira Configuration: URL, username, API token, version, and optional JQL.
  - Summarizer: Choose "huggingface", "openai", or "ollama" (provide OpenAI API key if needed).
  - Output: Select "file", "confluence", or both, and specify details (e.g., file path, Confluence credentials).
- Click "Generate Release Notes" to create the output.

### CLI Mode
Run the command-line interface:
```
docker run -it --network release-net -v $(pwd)/output:/app/output release-notes-app --cli
```
- Provide arguments or enter them interactively when prompted:
  - --jira-url: Jira instance URL (default: https://uat-givaudan.atlassian.net).
  - --jira-username: Jira username (required).
  - --jira-token: Jira API token (required).
  - --version: Release version (default: Test-release-0.1.0).
  - --jql: Custom JQL query (optional).
  - --summarizer: huggingface, openai, or ollama (default: huggingface).
  - --openai-api-key: Required for OpenAI summarizer.
  - --output: Space-separated list of file, confluence (default: file).
  - --file-path: Path for file output (default: output/release_notes.md).
  - --file-format: markdown, json, or html (default: markdown).
  - --confluence-url: Confluence URL (default: https://uat-givaudan.atlassian.net/wiki).
  - --confluence-username: Confluence username (required for Confluence).
  - --confluence-token: Confluence API token (required for Confluence).
  - --space-key: Confluence space key (default: FP).
  - --page-title: Confluence page title (default: Release Notes - {version}).
  - --parent-page-id: Confluence parent page ID (optional).
  
#### Example CLI Command
```
  docker run -it --network release-net -v $(pwd)/output:/app/output release-notes-app --cli --jira-username "user" --jira-token "token" --summarizer ollama --output file confluence --file-path "output/notes.md" --confluence-username "cuser" --confluence-token "ctoken"
```  

## Output
- File: Saved to the specified path (e.g., output/notes.md) in the mounted output/ directory.
- Confluence: Published to the specified space (e.g., FP) under the given page title.
  
## Troubleshooting
####  Streamlit Errors: If UI fails to load, check container logs:
```
  docker ps -a
  docker logs <container_id>
```

####  Ollama Connection: Ensure Ollama is running and accessible:
```
  docker ps  # Verify ollama container
```
Update summarizers/ollama_summarizer.py to use http://ollama:11434/api/generate if needed.
- Jira/Confluence Errors: Verify credentials and network access.
  
## Development Notes
*   Built with Python 3.9.
*   Dependencies managed via requirements.txt.
*   Streamlit UI runs on port 8501.
*   Ollama summarizer requires a separate container on the release-net network.

## Contributing
Feel free to submit issues or pull requests to enhance functionality or fix bugs!

---

### Instructions
1. **Create the File**:
   - Copy the content above into a text editor.
   - Save it as `README.md` in your project root directory (`arnr2/`).

2. **Customize**:
   - Replace `<repository-url>` with your actual Git repository URL if you’re using one.
   - Adjust default values (e.g., Jira URL, username) to match your specific setup if preferred.

3. **Include in Docker**:
   - The `COPY . .` line in your `Dockerfile` will automatically include `README.md` in the image, though it’s not required for runtime—it’s just documentation.

This Markdown file provides a comprehensive guide for your project, ensuring users can easily set up and use both the UI and CLI modes. Let me know if you’d like any additions or modifications!