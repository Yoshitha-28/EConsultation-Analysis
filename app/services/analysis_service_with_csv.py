# app/services/analysis_service_with_csv.py
from .analysis_service import analyze_comment_sync, analyze_text_directly
from ..utils.csv_logger import csv_logger
import logging

logger = logging.getLogger(__name__)

async def analyze_comment_sync_with_csv(db, comment_id: int, comment_text: str):
    """
    Wrapper around your existing analyze_comment_sync that adds CSV logging
    WITHOUT changing your core functionality
    """
    # Call your existing function exactly as it is
    result = await analyze_comment_sync(db, comment_id, comment_text)
    
    # Add CSV logging as a side effect (doesn't affect the return value)
    try:
        csv_logger.log_analysis_result(
            comment_id=comment_id,
            draft_id=result["draft_id"],
            comment_text=comment_text,
            analysis_result=result["analysis"]
        )
    except Exception as e:
        logger.error(f"CSV logging failed for comment {comment_id}: {e}")
        # Don't raise the error - CSV logging is optional
    
    return result  # Return the exact same result as your original function

async def analyze_text_directly_with_csv(text: str, draft_id: int = None):
    """
    Wrapper around your existing analyze_text_directly that adds CSV logging
    """
    result = await analyze_text_directly(text, draft_id)
    
    # Add CSV logging as a side effect
    try:
        csv_logger.log_analysis_result(
            comment_id=0,  # Use 0 for direct analysis without comment ID
            draft_id=draft_id or "direct_analysis",
            comment_text=text,
            analysis_result=result["analysis"]
        )
    except Exception as e:
        logger.error(f"CSV logging failed for direct analysis: {e}")
    
    return result