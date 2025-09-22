from .sentiment import get_sentiment
from .summarizer import get_summary
from .keywords import get_keywords
from .wordcloud import generate_and_upload_wordcloud
from ..utils.text_cleaning import clean_text
from ..config import settings
from datetime import datetime
import logging
import time

logger = logging.getLogger(__name__)

def analyze_text_pipeline(draft_id: str, text: str) -> dict:
    """Enhanced pipeline with better error handling and output formatting"""
    try:
        start_time = time.time()
        logger.info(f"Starting analysis pipeline for draft {draft_id}")
        
        cleaned_text = clean_text(text)
        logger.info(f"Text cleaning took: {time.time() - start_time:.2f}s")
        
        # Run analysis components with timing
        sentiment_start = time.time()
        sentiment_result = get_sentiment(cleaned_text)
        sentiment_time = time.time() - sentiment_start
        logger.info(f"Sentiment analysis took: {sentiment_time:.2f}s")
        
        summary_start = time.time()
        summary = get_summary(cleaned_text)
        summary_time = time.time() - summary_start
        logger.info(f"Summary generation took: {summary_time:.2f}s")
        
        keywords_start = time.time()
        keywords = get_keywords(cleaned_text)
        keywords_time = time.time() - keywords_start
        logger.info(f"Keyword extraction took: {keywords_time:.2f}s")
        
        wordcloud_start = time.time()
        wordcloud_path = generate_and_upload_wordcloud(draft_id, cleaned_text)
        wordcloud_time = time.time() - wordcloud_start
        logger.info(f"Wordcloud generation took: {wordcloud_time:.2f}s")
        
        total_time = time.time() - start_time
        logger.info(f"Total pipeline time: {total_time:.2f}s")
        
        # FIX: Use datetime object instead of ISO string
        analysis_result = {
            "sentiment_label": sentiment_result["label"],
            "sentiment_score": sentiment_result["score"],
            "summary": summary,
            "keywords": keywords,
            "wordcloud_path": wordcloud_path,
            "model_version": settings.MODEL_VERSION,
            "analyzed_at": datetime.utcnow()  # REMOVE .isoformat() - use datetime object
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
        "analyzed_at": datetime.utcnow()  # FIX: Remove .isoformat()
    }