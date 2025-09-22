from app.celery_app import celery_app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# --- New synchronous DB setup for the worker ---
from app.config import settings
from app import models, schemas, crud

sync_engine = create_engine(settings.DATABASE_URL_SYNC)
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
# --- End of new DB setup ---

import logging
from ..ml.pipeline import analyze_text_pipeline

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="app.workers.tasks.analyze_comment_async")
def analyze_comment_async(self, comment_id: int):
    logger.info(f"Starting analysis for comment_id: {comment_id}")

    db = SyncSessionLocal()
    try:
        # Get comment text
        comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
        if not comment:
            logger.error(f"Comment with id {comment_id} not found.")
            return {"error": "Comment not found"}

        comment.status = "processing"
        db.commit()

        # Run ML pipeline
        analysis_result = analyze_text_pipeline(draft_id=comment.draft_id, text=comment.text)

        # Create analysis entry
        analysis_create = schemas.CommentAnalysisCreate(**analysis_result)
        db_analysis = models.CommentAnalysis(**analysis_create.dict(), comment_id=comment_id)
        db.add(db_analysis)

        # Update status
        comment.status = "processed"
        db.commit()

        logger.info(f"Successfully analyzed comment_id: {comment_id}")
        return {"status": "success"}
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