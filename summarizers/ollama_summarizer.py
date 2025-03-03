import requests

# class OllamaSummarizer:
#     def __init__(self, url="http://ollama:11434/api/generate"):
#         self.url = url
#         self.model = "llama3.1"  # Default, overridden by CLI/config

class OllamaSummarizer:
    def __init__(self, url="http://host.docker.internal:11434/api/generate"):
        self.url = url
        self.model = "llama3.1"  # Default, overridden by CLI/config

    def summarize(self, text, version_name):
        truncated_text = text[:1000] if len(text) > 1000 else text  # Prevent overload
        payload = {
            "model": self.model,
            "prompt": f"Write a release notes summary for the following issues in '{version_name}'. Keep it concise and professional. Summarize in under 200 words.\n\n{truncated_text}",
            "stream": False
        }
        headers = {"Content-Type": "application/json"}
        print(f"DEBUG: Sending request to {self.url} with payload {payload}")
        response = requests.post(self.url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json().get("response", "Summarization failed")