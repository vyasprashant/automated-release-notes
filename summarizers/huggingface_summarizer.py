from transformers import pipeline

class HuggingFaceSummarizer:
    def __init__(self, model="sshleifer/distilbart-cnn-6-6"):  # Smaller model
        self.summarizer = pipeline("summarization", model=model)

    def summarize(self, text, max_length=300, min_length=80):
        input_length = len(text.split())
        max_length = min(300, max(100, int(input_length * 0.6)))
        min_length = max(80, int(max_length * 0.7))
        result = self.summarizer(text, max_length=max_length, min_length=min_length, do_sample=False, truncation=True)
        return result[0]["summary_text"]