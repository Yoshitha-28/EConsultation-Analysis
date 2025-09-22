from .sentiment import get_sentiment
from .summarizer import get_summary
from .keywords import get_keywords
from .wordcloud import generate_and_upload_wordcloud
from ..utils.text_cleaning import clean_text
from ..config import settings

def analyze_text_pipeline(draft_id: str, text: str) -> dict:
    cleaned_text = clean_text(text)
    sentiment = get_sentiment(cleaned_text)
    summary = get_summary(cleaned_text)
    keywords = get_keywords(cleaned_text)
    wordcloud_path = generate_and_upload_wordcloud(draft_id, cleaned_text)
    
    return {
        "sentiment": sentiment,
        "summary": summary,
        "keywords": keywords,
        "wordcloud_path": wordcloud_path,
        "model_version": settings.MODEL_VERSION
    }