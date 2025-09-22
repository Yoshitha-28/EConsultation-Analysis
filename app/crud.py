# app/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List
from . import models, schemas

async def create_comment(db: AsyncSession, comment: schemas.CommentCreate):
    db_comment = models.Comment(**comment.dict())
    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)
    return db_comment

async def create_comments(db: AsyncSession, comments: List[schemas.CommentCreate]):
    db_comments = [models.Comment(**comment.dict()) for comment in comments]
    db.add_all(db_comments)
    await db.commit()
    # Refresh each comment to get their IDs
    for comment in db_comments:
        await db.refresh(comment)
    return db_comments

async def get_comment(db: AsyncSession, comment_id: int):
    # FIX: Use selectinload to eagerly load the analysis relationship
    result = await db.execute(
        select(models.Comment)
        .options(selectinload(models.Comment.analysis))  # ← This is the fix
        .filter(models.Comment.id == comment_id)
    )
    return result.scalar_one_or_none()