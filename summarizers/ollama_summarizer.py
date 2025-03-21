import requests

class OllamaSummarizer:
    def __init__(self, url="http://host.docker.internal:11434/api/generate"):
        self.url = url

    def summarize(self, text, version_name):
        payload = {
            "model": "llama3.1",
            "prompt": f"Write a release notes summary for the following issues in '{version_name}'. Keep it concise and professional. Summarize in under 200 words.\n\n{text}",
            "stream": False
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(self.url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json().get("response", "Summarization failed")