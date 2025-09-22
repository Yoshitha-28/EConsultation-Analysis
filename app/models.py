# app/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    draft_id = Column(String, index=True)
    text = Column(String)
    user_id = Column(String, nullable=True)
    status = Column(String, default="received")
    submitted_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Ensure lazy loading is properly configured
    analysis = relationship("CommentAnalysis", back_populates="comment", 
                          uselist=False, cascade="all, delete-orphan", 
                          lazy="selectin")  # ← Change lazy loading strategy

class CommentAnalysis(Base):
    __tablename__ = "comment_analyses"
    id = Column(Integer, primary_key=True, index=True)
    sentiment_label = Column(String)
    sentiment_score = Column(Float)
    summary = Column(String)
    keywords = Column(ARRAY(String))
    wordcloud_path = Column(String, nullable=True)
    model_version = Column(String)
    analyzed_at = Column(DateTime, default=datetime.datetime.utcnow)
    comment_id = Column(Integer, ForeignKey("comments.id"))
    
    comment = relationship("Comment", back_populates="analysis")