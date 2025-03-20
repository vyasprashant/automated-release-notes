import streamlit as st
import yaml
from cli import generate_release_notes

def load_config(config_path="config.yaml"):
    """Load configuration from config.yaml and validate required fields."""
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        if not config:
            st.error("config.yaml is empty. Please provide a valid configuration.")
            raise ValueError("Empty config file")

        # Required top-level keys
        required_keys = ["jira", "version", "summarizer", "output"]
        missing = [key for key in required_keys if key not in config]
        if missing:
            st.error(f"Please add the following required keys to config.yaml and build the image again: {', '.join(missing)}")
            raise ValueError(f"Missing required keys: {missing}")

        # Required Jira fields
        required_jira = ["url", "username", "password"]
        missing_jira = [key for key in required_jira if key not in config["jira"]]
        if missing_jira:
            st.error(f"Please add the following keys to 'jira' in config.yaml and build the image again: {', '.join(missing_jira)}")
            raise ValueError(f"Missing Jira keys: {missing_jira}")

        # Required Summarizer fields
        if "type" not in config["summarizer"]:
            st.error("Please add 'type' to 'summarizer' in config.yaml and build the image again.")
            raise ValueError("Missing summarizer type")

        # Required Output fields
        required_output = ["type"]
        if "file" in config["output"]["type"]:
            required_output.extend(["file_path", "format"])
        missing_output = [key for key in required_output if key not in config["output"]]
        if missing_output:
            st.error(f"Please add the following keys to 'output' in config.yaml and build the image again: {', '.join(missing_output)}")
            raise ValueError(f"Missing output keys: {missing_output}")

        # Required Confluence fields if confluence is in output type
        if "confluence" in config["output"]["type"]:
            required_confluence = ["url", "username", "api_token", "space_key", "page_title"]
            missing_confluence = [key for key in required_confluence if key not in config["output"]["confluence"]]
            if missing_confluence:
                st.error(f"Please add the following keys to 'output.confluence' in config.yaml and build the image again: {', '.join(missing_confluence)}")
                raise ValueError(f"Missing confluence keys: {missing_confluence}")

        return config
    except FileNotFoundError:
        st.error("config.yaml not found. Please add config.yaml and build the image again.")
        raise
    except yaml.YAMLError as e:
        st.error(f"Invalid YAML in config.yaml: {str(e)}. Please fix config.yaml and build the image again.")
        raise

def main():
    # Load config
    try:
        cfg = load_config()
    except Exception:
        st.stop()  # Stop execution if config loading fails

    st.title("Release Notes Generator")

    st.subheader("Jira Configuration")
    jira_url = st.text_input("Jira URL", value=cfg["jira"]["url"])
    jira_username = st.text_input("Jira Username", value=cfg["jira"]["username"])
    jira_password = st.text_input("Jira API Token", type="password", value=cfg["jira"]["password"])
    version = st.text_input("Release Version", value=cfg["version"])
    jql = st.text_input("Custom JQL (optional)", placeholder="e.g., project = CICD", value=cfg["jira"].get("jql", ""))

    st.subheader("Summarizer Selection")
    summarizer = st.selectbox("Choose Summarizer", ["huggingface", "openai", "ollama"],
                              index=["huggingface", "openai", "ollama"].index(cfg["summarizer"]["type"]))
    openai_api_key = ""
    if summarizer == "openai":
        openai_api_key = st.text_input("OpenAI API Key", type="password", value=cfg["summarizer"].get("openai_api_key", ""))

    st.subheader("Output Options")
    output_types = st.multiselect("Output Types", ["file", "confluence"], default=cfg["output"]["type"])
    file_format = None
    file_path = None
    if "file" in output_types:
        file_format = st.selectbox("File Format", ["markdown", "json", "html"],
                                   index=["markdown", "json", "html"].index(cfg["output"]["format"]))
        default_file_path = cfg["output"]["file_path"].format(version=version, format=file_format)
        file_path = st.text_input("File Path", value=default_file_path)
    confluence_config = {}
    if "confluence" in output_types:
        confluence_cfg = cfg["output"]["confluence"]
        confluence_url = st.text_input("Confluence URL", value=confluence_cfg["url"])
        confluence_username = st.text_input("Confluence Username", value=confluence_cfg["username"])
        confluence_api_token = st.text_input("Confluence API Token", type="password", value=confluence_cfg["api_token"])
        space_key = st.text_input("Space Key", value=confluence_cfg["space_key"])
        default_page_title = confluence_cfg["page_title"].format(version=version)
        page_title = st.text_input("Page Title", value=default_page_title)
        parent_page_id = st.text_input("Parent Page ID (optional)", value=confluence_cfg.get("parent_page_id", ""))
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