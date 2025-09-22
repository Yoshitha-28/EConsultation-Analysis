from transformers import pipeline

# Define the pipeline as a global variable, but initialize it as None
_sentiment_pipeline = None

def get_sentiment(text: str) -> dict:
    global _sentiment_pipeline
    
    # THIS IS THE FIX:
    # The model is only loaded the very first time this function is called.
    if _sentiment_pipeline is None:
        print("Initializing sentiment analysis model...")
        _sentiment_pipeline = pipeline(
            "sentiment-analysis", 
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )
        print("Sentiment analysis model loaded.")

    # Truncate text to fit model's max input size
    result = _sentiment_pipeline(text[:512])[0] 
    return {"label": result["label"].lower(), "score": round(result["score"], 4)}