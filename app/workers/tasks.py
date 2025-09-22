from app.celery_app import celery_app
from bson import ObjectId
import logging
from datetime import datetime
from ..db import db_sync
from ..ml.pipeline import analyze_text_pipeline

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="app.workers.tasks.analyze_comment_async")
def analyze_comment_async(self, comment_id: str):
    """
    Celery task to run the full NLP pipeline on a comment.
    """
    logger.info(f"Starting analysis for comment_id: {comment_id}")
    comment_oid = ObjectId(comment_id)
    
    db_sync.comments.update_one({"_id": comment_oid}, {"$set": {"status": "processing"}})
    
    comment = db_sync.comments.find_one({"_id": comment_oid})
    if not comment:
        logger.error(f"Comment with id {comment_id} not found.")
        return {"error": "Comment not found"}

    try:
        analysis_result = analyze_text_pipeline(draft_id=comment["draft_id"], text=comment["text"])
        analysis_doc = {"comment_id": comment_oid, "draft_id": comment["draft_id"], "analyzed_at": datetime.utcnow(), **analysis_result}
        db_sync.comment_analysis.insert_one(analysis_doc)
        db_sync.comments.update_one({"_id": comment_oid}, {"$set": {"status": "processed"}})
        logger.info(f"Successfully analyzed comment_id: {comment_id}")
        return {"status": "success", "comment_id": comment_id}

    except Exception as e:
        logger.exception(f"Error analyzing comment_id: {comment_id}")
        db_sync.comments.update_one({"_id": comment_oid}, {"$set": {"status": "error", "error_message": str(e)}})
        raise