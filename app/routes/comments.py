from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from .. import crud, schemas
from ..database import AsyncSessionLocal
from ..celery_app import celery_app

router = APIRouter()

# Dependency to get DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/comments/bulk", response_model=schemas.BulkCommentsResponse)
async def create_bulk_comments(payload: schemas.BulkCommentsIn, db: AsyncSession = Depends(get_db)):
    comments_to_create = [schemas.CommentCreate(draft_id=payload.draft_id, text=t) for t in payload.comments]
    
    if not comments_to_create:
        raise HTTPException(status_code=400, detail="Comments list cannot be empty.")
    
    created_comments = await crud.create_comments(db, comments_to_create)
    
    task_ids = []
    for comment in created_comments:
        # This line sends the task by name to the worker
        task = celery_app.send_task("app.workers.tasks.analyze_comment_async", args=[comment.id])
        task_ids.append(task.id)
        
    return {
        "message": f"Successfully received and queued {len(created_comments)} comments for analysis.",
        "draft_id": payload.draft_id,
        "comments_received": len(created_comments),
        "task_ids": task_ids,
    }

@router.get("/comments/{comment_id}", response_model=schemas.Comment)
async def read_comment(comment_id: int, db: AsyncSession = Depends(get_db)):
    db_comment = await crud.get_comment(db, comment_id=comment_id)
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return db_comment