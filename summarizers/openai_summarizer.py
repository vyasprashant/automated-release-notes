from openai import OpenAI

class OpenAISummarizer:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def summarize(self, text, max_words=200):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a concise summarizer for release notes."},
                {"role": "user", "content": f"Summarize the following text in under {max_words} words:\n\n{text}"}
            ],
            max_tokens=300,
            temperature=0.5
        )
        return response.choices[0].message.content.strip()