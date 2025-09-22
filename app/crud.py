from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload # <--- ADD THIS IMPORT
from . import models, schemas

async def get_comment(db: AsyncSession, comment_id: int):
    # THIS IS THE FIX:
    # We add .options(selectinload(...)) to eagerly load the relationship
    query = select(models.Comment).options(selectinload(models.Comment.analysis)).filter(models.Comment.id == comment_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def create_comments(db: AsyncSession, comments: List[schemas.CommentCreate]):
    db_comments = [models.Comment(**c.dict()) for c in comments]
    db.add_all(db_comments)
    await db.commit()
    for db_comment in db_comments:
        await db.refresh(db_comment)
    return db_comments