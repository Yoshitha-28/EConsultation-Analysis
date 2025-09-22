from transformers import pipeline
from typing import Dict
import logging

logger = logging.getLogger(__name__)

_sentiment_pipeline = None

def get_sentiment(text: str) -> Dict:
    global _sentiment_pipeline
    try:
        if _sentiment_pipeline is None:
            _sentiment_pipeline = pipeline(
                "sentiment-analysis", 
                model="distilbert-base-uncased-finetuned-sst-2-english",
                truncation=True,
                max_length=512
            )
        
        if not text or not text.strip():
            return {"label": "neutral", "score": 0.5}
        
        # Ensure text is properly truncated
        truncated_text = text[:512]
        result = _sentiment_pipeline(truncated_text)[0]
        
        # Map to consistent label format and ensure proper scoring
        label = result["label"].lower()
        score = round(float(result["score"]), 4)
        
        # For the specific example comment, we expect negative sentiment
        # Let's add some debugging to verify
        test_comment = "The ethical guidelines section is comprehensive but lacks clear enforcement mechanisms."
        if "lacks" in text.lower() or "oversight" in text.lower():
            logger.info(f"Debug - Analyzing critical comment: {text[:100]}...")
            logger.info(f"Debug - Result: {result}")
        
        return {"label": label, "score": score}
        
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")
        # Fallback sentiment analysis
        return fallback_sentiment_analysis(text)

def fallback_sentiment_analysis(text: str) -> Dict:
    """Fallback when transformer model fails"""
    text_lower = text.lower()
    
    # More sophisticated fallback logic
    negative_indicators = ['lack', 'insufficient', 'no mention', 'critical', 'oversight', 
                          'ineffective', 'must be addressed', 'problem', 'issue']
    positive_indicators = ['comprehensive', 'support', 'good', 'excellent', 'effective', 'well']
    
    negative_count = sum(1 for word in negative_indicators if word in text_lower)
    positive_count = sum(1 for word in positive_indicators if word in text_lower)
    
    if negative_count > positive_count:
        return {"label": "negative", "score": 0.85}
    elif positive_count > negative_count:
        return {"label": "positive", "score": 0.85}
    else:
        return {"label": "neutral", "score": 0.5}