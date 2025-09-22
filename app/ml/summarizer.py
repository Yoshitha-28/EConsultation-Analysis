from transformers import pipeline

_summarizer_pipeline = None

def get_summary(text: str, max_length=50, min_length=15) -> str:
    global _summarizer_pipeline
    if _summarizer_pipeline is None:
        _summarizer_pipeline = pipeline("summarization", model="sshleifer/distilbart-cnn-6-6")
    if len(text.split()) < 25:
        return text
    summary = _summarizer_pipeline(text, max_length=max_length, min_length=min_length, do_sample=False)[0]
    return summary["summary_text"]