from transformers import pipeline

_sentiment_pipeline = None

def get_sentiment(text: str) -> dict:
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        _sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
    result = _sentiment_pipeline(text[:512])[0] 
    return {"label": result["label"].lower(), "score": round(result["score"], 4)}