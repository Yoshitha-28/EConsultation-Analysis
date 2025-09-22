# app/services/analysis_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app import models, schemas
from ..ml.pipeline import analyze_text_pipeline
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

async def analyze_comment_sync(db: AsyncSession, comment_id: int, comment_text: str):
    """
    Perform synchronous analysis for a comment and return the results immediately
    """
    try:
        logger.info(f"Starting synchronous analysis for comment_id: {comment_id}")
        
        # Get the comment from database
        stmt = select(models.Comment).where(models.Comment.id == comment_id)
        result = await db.execute(stmt)
        comment = result.scalar_one_or_none()
        
        if not comment:
            logger.error(f"Comment with id {comment_id} not found.")
            raise ValueError(f"Comment with id {comment_id} not found")

        # Update status to processing
        comment.status = "processing"
        await db.commit()

        # Run analysis pipeline synchronously
        analysis_result = analyze_text_pipeline(draft_id=comment.draft_id, text=comment_text)
        
        # Create analysis record with proper field mapping
        analysis_data = {
            "sentiment_label": analysis_result["sentiment_label"],
            "sentiment_score": analysis_result["sentiment_score"],
            "summary": analysis_result["summary"],
            "keywords": analysis_result["keywords"],
            "wordcloud_path": analysis_result["wordcloud_path"],
            "model_version": analysis_result["model_version"],
            "analyzed_at": analysis_result["analyzed_at"],
            "comment_id": comment_id
        }
        
        db_analysis = models.CommentAnalysis(**analysis_data)
        db.add(db_analysis)
        
        # Update comment status
        comment.status = "processed"
        await db.commit()

        logger.info(f"Successfully analyzed comment_id: {comment_id}. Sentiment: {analysis_result['sentiment_label']}")
        
        # Return the complete analysis results
        return {
            "comment_id": comment_id,
            "draft_id": comment.draft_id,
            "status": "processed",
            "analysis": {
                "sentiment_label": analysis_result["sentiment_label"],
                "sentiment_score": analysis_result["sentiment_score"],
                "summary": analysis_result["summary"],
                "keywords": analysis_result["keywords"],
                "wordcloud_path": analysis_result["wordcloud_path"],
                "model_version": analysis_result["model_version"],
                "analyzed_at": analysis_result["analyzed_at"].isoformat() if hasattr(analysis_result["analyzed_at"], 'isoformat') else datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error analyzing comment_id: {comment_id}: {str(e)}")
        
        # Update comment status to error
        if comment:
            comment.status = "error"
            await db.commit()
        
        # Re-raise the exception to be handled by the route
        raise e

async def analyze_text_directly(text: str, draft_id: int = None):
    """
    Alternative function to analyze text without database operations
    Useful for simple synchronous analysis without storing results
    """
    try:
        logger.info(f"Analyzing text directly for draft_id: {draft_id}")
        
        # Run analysis pipeline synchronously
        analysis_result = analyze_text_pipeline(draft_id=draft_id, text=text)
        
        # Return the complete analysis results
        return {
            "draft_id": draft_id,
            "text": text,
            "status": "analyzed",
            "analysis": {
                "sentiment_label": analysis_result["sentiment_label"],
                "sentiment_score": analysis_result["sentiment_score"],
                "summary": analysis_result["summary"],
                "keywords": analysis_result["keywords"],
                "wordcloud_path": analysis_result["wordcloud_path"],
                "model_version": analysis_result["model_version"],
                "analyzed_at": analysis_result["analyzed_at"].isoformat() if analysis_result["analyzed_at"] else datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error analyzing text: {str(e)}")
        raise e