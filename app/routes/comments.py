from fastapi import APIRouter, HTTPException, status
from typing import List
from bson import ObjectId
from datetime import datetime
from ..db import db_async
from ..models import Comment, CommentOut, BulkCommentsIn, BulkCommentsResponse
from ..workers.tasks import analyze_comment_async

router = APIRouter()

@router.post("/comments/bulk", response_model=BulkCommentsResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_bulk_comments(payload: BulkCommentsIn):
    """
    Accept a list of comments for a single draft, save them,
    and trigger analysis tasks for each one.
    """
    task_ids = []
    comments_to_insert = []

    # Loop through the comment texts and create a full document for each one
    for comment_text in payload.comments:
        # Manually create the document dictionary and assign a NEW ObjectId
        comment_doc = {
            "_id": ObjectId(), # <--- THIS IS THE FIX: Generate a new unique ID
            "draft_id": payload.draft_id,
            "text": comment_text,
            "user_id": None, # Assuming no user_id for bulk
            "status": "received",
            "submitted_at": datetime.utcnow()
        }
        comments_to_insert.append(comment_doc)

    if not comments_to_insert:
        raise HTTPException(status_code=400, detail="Comments list cannot be empty.")

    # Insert all comments in a single database operation
    result = await db_async.comments.insert_many(comments_to_insert)
    inserted_ids = result.inserted_ids

    # Trigger a Celery task for each newly inserted comment
    for comment_id in inserted_ids:
        task = analyze_comment_async.delay(str(comment_id))
        task_ids.append(task.id)

    return {
        "message": f"Successfully received and queued {len(inserted_ids)} comments for analysis.",
        "draft_id": payload.draft_id,
        "comments_received": len(inserted_ids),
        "task_ids": task_ids,
    }

@router.get("/comments/{comment_id}", response_model=CommentOut)
async def get_comment(comment_id: str):
    if not ObjectId.is_valid(comment_id):
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")
        
    comment_oid = ObjectId(comment_id)
    comment = await db_async.comments.find_one({"_id": comment_oid})
    
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")

    analysis = await db_async.comment_analysis.find_one({"comment_id": comment_oid})
    
    response = CommentOut(**comment)
    if analysis:
        response.analysis = analysis
        
    return response