from transformers import pipeline
from typing import Dict
import logging

logger = logging.getLogger(__name__)

_sentiment_pipeline = None

def get_sentiment(text: str) -> Dict:
    """
    Analyzes sentiment and infers neutrality if the model's confidence
    is below a defined threshold.
    """
    global _sentiment_pipeline
    
    # This is the threshold for determining neutrality. You can adjust it.
    # A higher value (e.g., 0.95) means more text will be classified as neutral.
    # A lower value (e.g., 0.70) means less text will be classified as neutral.
    NEUTRALITY_THRESHOLD = 0.80

    try:
        if _sentiment_pipeline is None:
            _sentiment_pipeline = pipeline(
                "sentiment-analysis", 
                model="distilbert-base-uncased-finetuned-sst-2-english",
                truncation=True,
                max_length=512
            )
        
        if not text or not text.strip():
            return {"label": "neutral", "score": 1.0}
        
        # The pipeline handles truncation automatically
        result = _sentiment_pipeline(text)[0]
        
        label = result["label"].lower()
        score = round(float(result["score"]), 4)
        
        # --- THIS IS THE NEW LOGIC FOR NEUTRALITY ---
        # If the model's confidence score is below our threshold,
        # we override its prediction and classify it as "neutral".
        if score < NEUTRALITY_THRESHOLD:
            label = "neutral"
        # ---------------------------------------------
            
        return {"label": label, "score": score}
        
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")
        return fallback_sentiment_analysis(text)

def fallback_sentiment_analysis(text: str) -> Dict:
    """Fallback when transformer model fails"""
    text_lower = text.lower()
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