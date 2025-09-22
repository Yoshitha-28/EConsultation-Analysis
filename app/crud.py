from typing import List # <--- THIS IS THE FIX
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from . import models, schemas

async def get_comment(db: AsyncSession, comment_id: int):
    result = await db.execute(select(models.Comment).filter(models.Comment.id == comment_id))
    return result.scalar_one_or_none()

async def create_comments(db: AsyncSession, comments: List[schemas.CommentCreate]):
    db_comments = [models.Comment(**c.dict()) for c in comments]
    db.add_all(db_comments)
    await db.commit()
    for db_comment in db_comments:
        await db.refresh(db_comment)
    return db_comments

async def create_comment_analysis(db: AsyncSession, analysis: schemas.CommentAnalysisCreate, comment_id: int):
    db_analysis = models.CommentAnalysis(**analysis.dict(), comment_id=comment_id)
    db.add(db_analysis)
    await db.commit()
    await db.refresh(db_analysis)
    return db_analysis

async def update_comment_status(db: AsyncSession, comment_id: int, status: str):
    comment = await get_comment(db, comment_id)
    if comment:
        comment.status = status
        await db.commit()
        await db.refresh(comment)
    return comment