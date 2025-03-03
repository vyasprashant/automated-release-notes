import streamlit as st
from cli import generate_release_notes

def main():
    st.title("Release Notes Generator")

    st.subheader("Jira Configuration")
    jira_url = st.text_input("Jira URL", value="https://uat-givaudan.atlassian.net")
    jira_username = st.text_input("Jira Username", value="your-email@example.com")
    jira_password = st.text_input("Jira API Token", type="password")
    version = st.text_input("Release Version", value="Test-release-0.1.0")
    jql = st.text_input("Custom JQL (optional)", placeholder="e.g., project = CICD", value="")

    st.subheader("Summarizer Selection")
    summarizer = st.selectbox("Choose Summarizer", ["huggingface", "openai", "ollama"])
    openai_api_key = ""
    if summarizer == "openai":
        openai_api_key = st.text_input("OpenAI API Key", type="password")

    st.subheader("Output Options")
    output_types = st.multiselect("Output Types", ["file", "confluence"], default=["file"])
    file_format = None
    file_path = None
    if "file" in output_types:
        file_format = st.selectbox("File Format", ["markdown", "json", "html"], index=0)
        file_path = st.text_input("File Path", value=f"output/release_notes_{version}.{file_format}")
    confluence_config = {}
    if "confluence" in output_types:
        confluence_url = st.text_input("Confluence URL", value="https://uat-givaudan.atlassian.net/wiki")
        confluence_username = st.text_input("Confluence Username")
        confluence_api_token = st.text_input("Confluence API Token", type="password")
        space_key = st.text_input("Space Key", value="FP")
        page_title = st.text_input("Page Title", value=f"Release Notes - {version}")
        parent_page_id = st.text_input("Parent Page ID (optional)", value="181600450")
        confluence_config = {
            "url": confluence_url,
            "username": confluence_username,
            "api_token": confluence_api_token,
            "space_key": space_key,
            "page_title": page_title,
            "parent_page_id": parent_page_id if parent_page_id else None
        }

    if st.button("Generate Release Notes"):
        cfg = {
            "jira": {
                "url": jira_url,
                "username": jira_username,
                "password": jira_password,
            },
            "version": version,
            "summarizer": {
                "type": summarizer
            },
            "output": {
                "type": output_types
            }
        }
        if jql:
            cfg["jira"]["jql"] = jql
        if summarizer == "openai" and openai_api_key:
            cfg["summarizer"]["openai_api_key"] = openai_api_key
        if "file" in output_types:
            cfg["output"]["file_path"] = file_path
            cfg["output"]["format"] = file_format
        if "confluence" in output_types:
            cfg["output"]["confluence"] = confluence_config

        with st.spinner("Generating release notes..."):
            try:
                generate_release_notes(cfg)
                st.success("Release notes generated successfully!")
                if "file" in output_types:
                    st.write(f"File saved to: {file_path}")
                if "confluence" in output_types:
                    st.write("Check Confluence for the published page.")
            except Exception as e:
                st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()