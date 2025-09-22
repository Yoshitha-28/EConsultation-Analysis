# app/routes/comments.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from .. import models, schemas
from ..crud import create_comments, get_comment
# Change only this import - use the CSV wrapper instead of direct service
from ..services.analysis_service_with_csv import analyze_comment_sync_with_csv as analyze_comment_sync

router = APIRouter()

@router.post("/comments/bulk", response_model=schemas.BulkCommentsResponse)
async def create_bulk_comments(
    payload: schemas.BulkCommentsIn, 
    db: AsyncSession = Depends(get_db)
):
    """Create multiple comments and perform analysis synchronously"""
    try:
        # Create comments using your existing crud function (NO CHANGES)
        comments_to_create = [
            schemas.CommentCreate(draft_id=payload.draft_id, text=text) 
            for text in payload.comments
        ]
        
        # Create comments in database (NO CHANGES)
        created_comments = await create_comments(db, comments_to_create)
        
        # Perform analysis synchronously for each comment 
        # (ONLY CHANGE: now calls the wrapper function which internally calls your original function)
        analysis_results = []
        for comment in created_comments:
            # This calls your original analyze_comment_sync through the wrapper
            analysis_result = await analyze_comment_sync(db, comment.id, comment.text)
            analysis_results.append(analysis_result)
            
            # Update comment status (your existing logic)
            comment.status = "processed"
        
        await db.commit()  # Your existing commit
        
        return {
            "message": f"Successfully analyzed {len(created_comments)} comments.",
            "draft_id": payload.draft_id,
            "comments_received": len(created_comments),
            "analysis_results": analysis_results,
        }
        
    except Exception as e:
        await db.rollback()  # Your existing rollback
        raise HTTPException(status_code=500, detail=f"Failed to analyze comments: {str(e)}")

# KEEP ALL YOUR EXISTING GET ENDPOINTS EXACTLY THE SAME
@router.get("/comments/{comment_id}", response_model=schemas.Comment)
async def read_comment(comment_id: int, db: AsyncSession = Depends(get_db)):
    """Get a comment with its analysis"""
    db_comment = await get_comment(db, comment_id=comment_id)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    return db_comment

@router.get("/comments/{comment_id}/analysis")
async def get_analysis_result(comment_id: int, db: AsyncSession = Depends(get_db)):
    """Get analysis results for a comment"""
    try:
        comment = await get_comment(db, comment_id=comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")
        
        analysis_result = comment.analysis
        
        if not analysis_result:
            raise HTTPException(status_code=404, detail="Analysis not yet completed")
        
        return {
            "draft_id": comment.draft_id,
            "text": comment.text,
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