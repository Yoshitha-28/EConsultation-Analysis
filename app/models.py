import uuid
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base

class UserRole(enum.Enum):
    stakeholder = "stakeholder"
    admin = "admin"

class SentimentType(enum.Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.stakeholder)
    created_at = Column(DateTime, default=datetime.utcnow)

    comments = relationship("Comment", back_populates="user")

class Draft(Base):
    __tablename__ = "drafts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    open_date = Column(DateTime, nullable=False)
    close_date = Column(DateTime, nullable=False)

    comments = relationship("Comment", back_populates="draft")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    draft_id = Column(UUID(as_uuid=True), ForeignKey("drafts.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    draft = relationship("Draft", back_populates="comments")
    user = relationship("User", back_populates="comments")
    analysis = relationship("Analysis", uselist=False, back_populates="comment")

class Analysis(Base):
    __tablename__ = "analysis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    comment_id = Column(UUID(as_uuid=True), ForeignKey("comments.id"), nullable=False)
    sentiment = Column(Enum(SentimentType))
    summary = Column(Text)
    keywords = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    comment = relationship("Comment", back_populates="analysis")
