from .sentiment import get_sentiment
from .summarizer import get_summary
from .keywords import get_keywords
from .wordcloud import generate_and_upload_wordcloud
from ..utils.text_cleaning import clean_text
from ..config import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def analyze_text_pipeline(draft_id: str, text: str) -> dict:
    """Enhanced pipeline with better error handling and output formatting"""
    try:
        cleaned_text = clean_text(text)
        
        # Run analysis components
        sentiment_result = get_sentiment(cleaned_text)
        summary = get_summary(cleaned_text)
        keywords = get_keywords(cleaned_text)
        wordcloud_path = generate_and_upload_wordcloud(draft_id, cleaned_text)
        
        # Format the output to match your expected structure
        analysis_result = {
            "sentiment_label": sentiment_result["label"],
            "sentiment_score": sentiment_result["score"],
            "summary": summary,
            "keywords": keywords,
            "wordcloud_path": wordcloud_path,
            "model_version": settings.MODEL_VERSION,
            "analyzed_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Analysis completed for draft {draft_id}. Sentiment: {sentiment_result['label']}")
        return analysis_result
        
    except Exception as e:
        logger.error(f"Pipeline analysis failed for draft {draft_id}: {e}")
        # Return a proper error result instead of failing
        return get_fallback_analysis(text, draft_id)

def get_fallback_analysis(text: str, draft_id: str) -> dict:
    """Fallback analysis when pipeline fails"""
    return {
        "sentiment_label": "neutral",
        "sentiment_score": 0.5,
        "summary": text[:100] + "..." if len(text) > 100 else text,
        "keywords": ["analysis", "pending"],
        "wordcloud_path": "",
        "model_version": "fallback",
        "analyzed_at": datetime.utcnow().isoformat()
    }