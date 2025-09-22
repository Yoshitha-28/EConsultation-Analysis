from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

# --- Analysis Schemas ---
class CommentAnalysisBase(BaseModel):
    sentiment_label: str
    sentiment_score: float
    summary: str
    keywords: List[str]
    wordcloud_path: Optional[str] = None
    model_version: str

class CommentAnalysisCreate(CommentAnalysisBase):
    pass

class CommentAnalysis(CommentAnalysisBase):
    id: int
    comment_id: int
    analyzed_at: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Comment Schemas ---
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
    model_config = ConfigDict(from_attributes=True)

# --- Bulk Input Schemas ---
class BulkCommentsIn(BaseModel):
    draft_id: str
    comments: List[str]

class BulkCommentsResponse(BaseModel):
    message: str
    draft_id: str
    comments_received: int
    task_ids: List[str]