from app.celery_app import celery_app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# We import the Settings CLASS, not the instance
from app.config import Settings
from app import models, schemas
from ..ml.pipeline import analyze_text_pipeline
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="app.workers.tasks.analyze_comment_async")
def analyze_comment_async(self, comment_id: int):
    # THIS IS THE FIX: Create the settings object and DB session INSIDE the task
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

        comment.status = "processing"
        db.commit()

        analysis_result = analyze_text_pipeline(draft_id=comment.draft_id, text=comment.text)
        analysis_create = schemas.CommentAnalysisCreate(**analysis_result)
        db_analysis = models.CommentAnalysis(**analysis_create.dict(), comment_id=comment_id)
        db.add(db_analysis)
        
        comment.status = "processed"
        db.commit()

        logger.info(f"Successfully analyzed comment_id: {comment_id}")
    except Exception as e:
        db.rollback()
        logger.exception(f"Error analyzing comment_id: {comment_id}")
        comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
        if comment:
            comment.status = "error"
            db.commit()
        raise
    finally:
        db.close()