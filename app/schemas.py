# app/schemas.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CommentAnalysisBase(BaseModel):
    sentiment_label: str
    sentiment_score: float
    summary: str
    keywords: List[str]
    wordcloud_path: Optional[str] = None
    model_version: str
    analyzed_at: datetime

class CommentAnalysisCreate(CommentAnalysisBase):
    pass

class CommentAnalysis(CommentAnalysisBase):
    id: int
    comment_id: int
    
    class Config:
        from_attributes = True

class CommentBase(BaseModel):
    draft_id: str
    text: str
    user_id: Optional[str] = None

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    status: str
    submitted_at: datetime
    analysis: Optional[CommentAnalysis] = None
    
    class Config:
        from_attributes = True

class BulkCommentsIn(BaseModel):
    draft_id: str
    comments: List[str]

class BulkCommentsResponse(BaseModel):
    message: str
    draft_id: str
    comments_received: int
    task_ids: List[str]