from transformers import pipeline

# Define the pipeline as a global variable, but initialize it as None
_summarizer_pipeline = None

def get_summary(text: str, max_length=50, min_length=15) -> str:
    global _summarizer_pipeline

    # THIS IS THE FIX:
    # The model is only loaded the very first time this function is called.
    if _summarizer_pipeline is None:
        print("Initializing summarization model...")
        _summarizer_pipeline = pipeline(
            "summarization", 
            model="sshleifer/distilbart-cnn-6-6"
        )
        print("Summarization model loaded.")
    
    # If text is short, return it as is.
    if len(text.split()) < 25:
        return text
    
    summary = _summarizer_pipeline(
        text, 
        max_length=max_length, 
        min_length=min_length, 
        do_sample=False
    )[0]
    return summary["summary_text"]