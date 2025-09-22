# app/schemas.py
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
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

# NEW: Schema for individual analysis result
class CommentAnalysisResult(BaseModel):
    comment_id: int
    draft_id: str
    status: str
    analysis: Dict[str, Any]

# UPDATED: Now returns analysis results instead of task IDs
class BulkCommentsResponse(BaseModel):
    message: str
    draft_id: str
    comments_received: int
    analysis_results: List[CommentAnalysisResult]  # Changed from task_ids to analysis_results

# NEW: Schema for direct text analysis (optional)
class DirectAnalysisRequest(BaseModel):
    text: str
    draft_id: Optional[str] = None

class DirectAnalysisResponse(BaseModel):
    draft_id: Optional[str]
    text: str
    status: str
    analysis: Dict[str, Any]