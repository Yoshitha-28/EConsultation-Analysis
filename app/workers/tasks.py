from app.celery_app import celery_app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import Settings
from app import models, schemas
from ..ml.pipeline import analyze_text_pipeline
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="app.workers.tasks.analyze_comment_async")
def analyze_comment_async(self, comment_id: int):
    settings = Settings()
    sync_engine = create_engine(settings.DATABASE_URL_SYNC)
    SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
    
    logger.info(f"Starting analysis for comment_id: {comment_id}")
    db = SyncSessionLocal()
    try:
        comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
        if not comment:
            logger.error(f"Comment with id {comment_id} not found.")
            return

        # Update status to processing
        comment.status = "processing"
        db.commit()

        # Run analysis pipeline
        analysis_result = analyze_text_pipeline(draft_id=comment.draft_id, text=comment.text)
        
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
        db.commit()

        logger.info(f"Successfully analyzed comment_id: {comment_id}. Sentiment: {analysis_result['sentiment_label']}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error analyzing comment_id: {comment_id}: {str(e)}")
        
        # Update comment status to error
        comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
        if comment:
            comment.status = "error"
            db.commit()
        
        # Retry the task after 60 seconds
        raise self.retry(exc=e, countdown=60)
    finally:
        db.close()