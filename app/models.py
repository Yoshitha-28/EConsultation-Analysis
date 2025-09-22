from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, (str, __import__("bson").ObjectId)):
            raise TypeError('ObjectId required')
        return str(v)

class Sentiment(BaseModel):
    label: str
    score: float

class CommentAnalysis(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    comment_id: PyObjectId
    draft_id: str
    sentiment: Sentiment
    summary: str
    keywords: List[str]
    wordcloud_path: Optional[str] = None
    model_version: str
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {__import__("bson").ObjectId: str}
        allow_population_by_field_name = True

class Comment(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    draft_id: str
    text: str
    user_id: Optional[str] = None
    status: str = "received"
    submitted_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {__import__("bson").ObjectId: str}
        allow_population_by_field_name = True

class CommentOut(Comment):
    analysis: Optional[CommentAnalysis] = None

class BulkCommentsIn(BaseModel):
    draft_id: str = Field(..., example="New_IT_Rules_2025")
    comments: List[str] = Field(..., min_items=1, example=["Comment 1.", "Comment 2."])

class BulkCommentsResponse(BaseModel):
    message: str
    draft_id: str
    comments_received: int
    task_ids: List[str]