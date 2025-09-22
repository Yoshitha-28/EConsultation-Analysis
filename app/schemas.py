from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
import uuid

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    role: str
    created_at: datetime
    class Config:
        orm_mode = True

class DraftCreate(BaseModel):
    title: str
    description: str
    open_date: datetime
    close_date: datetime

class DraftOut(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    open_date: datetime
    close_date: datetime
    class Config:
        orm_mode = True

class CommentCreate(BaseModel):
    text: str

class CommentOut(BaseModel):
    id: uuid.UUID
    text: str
    created_at: datetime
    user: UserOut
    class Config:
        orm_mode = True

class AnalysisOut(BaseModel):
    sentiment: str
    summary: str
    keywords: List[str]
    class Config:
        orm_mode = True
