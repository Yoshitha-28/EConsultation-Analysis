# app/routes/comments.py
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from .. import models, schemas
from ..crud import create_comments, get_comment  # ← Change to create_comments (plural)
from app.workers.tasks import analyze_comment_async

router = APIRouter()

@router.post("/comments/bulk", response_model=schemas.BulkCommentsResponse)
async def create_bulk_comments(
    payload: schemas.BulkCommentsIn, 
    db: AsyncSession = Depends(get_db)
):
    """Create multiple comments and start analysis"""
    try:
        # Create comments using your existing crud function
        comments_to_create = [
            schemas.CommentCreate(draft_id=payload.draft_id, text=text) 
            for text in payload.comments
        ]
        
        # FIX: Use create_comments (plural) instead of create_comment (singular)
        created_comments = await create_comments(db, comments_to_create)  # ← This is correct now
        
        task_ids = []
        for comment in created_comments:
            task = analyze_comment_async.delay(comment.id)
            task_ids.append(task.id)
        
        return {
            "message": f"Successfully received and queued {len(created_comments)} comments for analysis.",
            "draft_id": payload.draft_id,
            "comments_received": len(created_comments),
            "task_ids": task_ids,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create comments: {str(e)}")

@router.get("/comments/{comment_id}", response_model=schemas.Comment)
async def read_comment(comment_id: int, db: AsyncSession = Depends(get_db)):
    """Get a comment with its analysis"""
    db_comment = await get_comment(db, comment_id=comment_id)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Convert to response model - the relationship is called "analysis" not "analysis_result"
    return db_comment

@router.get("/comments/{comment_id}/analysis")
async def get_analysis_result(comment_id: int, db: AsyncSession = Depends(get_db)):
    """Get analysis results for a comment"""
    try:
        comment = await get_comment(db, comment_id=comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        # The relationship is called "analysis" (singular) based on your model
        analysis_result = comment.analysis  # NOT analysis_result
        
        if not analysis_result:
            raise HTTPException(status_code=404, detail="Analysis not yet completed")
        
        return {
            "draft_id": comment.draft_id,
            "text": comment.text,
            "user_id": comment.user_id,
            "id": comment.id,
            "status": comment.status,
            "submitted_at": comment.submitted_at.isoformat(),
            "analysis": {
                "id": analysis_result.id,
                "comment_id": comment_id,
                "sentiment_label": analysis_result.sentiment_label,
                "sentiment_score": analysis_result.sentiment_score,
                "summary": analysis_result.summary,
                "keywords": analysis_result.keywords,
                "wordcloud_path": analysis_result.wordcloud_path,
                "model_version": analysis_result.model_version,
                "analyzed_at": analysis_result.analyzed_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analysis: {str(e)}")