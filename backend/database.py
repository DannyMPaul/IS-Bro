from sqlalchemy import (
    create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Boolean,
    Float, Table
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timezone
import os

DATABASE_URL = "sqlite:///./conversations.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)
    
    conversations = relationship("Conversation", back_populates="user")

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String, default="New Chat")
    stage = Column(String, default="initial")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    pinned = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable for backward compatibility
    
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    user = relationship("User", back_populates="conversations")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String, ForeignKey("conversations.id"))
    role = Column(String)  # "user" or "assistant"
    content = Column(Text)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    suggestions = Column(Text, nullable=True)  # JSON string
    
    conversation = relationship("Conversation", back_populates="messages")

# Association tables for many-to-many relationships
summary_tags = Table('summary_tags', Base.metadata,
    Column('summary_id', Integer, ForeignKey('conversation_summaries.id')),
    Column('tag_id', Integer, ForeignKey('idea_tags.id'))
)

summary_categories = Table('summary_categories', Base.metadata,
    Column('summary_id', Integer, ForeignKey('conversation_summaries.id')),
    Column('category_id', Integer, ForeignKey('idea_categories.id'))
)

class ConversationSummary(Base):
    __tablename__ = "conversation_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String, ForeignKey("conversations.id"))
    summary_type = Column(String)  # 'brief', 'detailed', 'technical', 'action_items'
    content = Column(Text)
    key_points = Column(Text)  # JSON string of key points
    sentiment_score = Column(Float)
    completion_percentage = Column(Float)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    conversation = relationship("Conversation", back_populates="summaries")
    tags = relationship("IdeaTag", secondary=summary_tags, back_populates="summaries")
    categories = relationship("IdeaCategory", secondary=summary_categories, back_populates="summaries")

class IdeaCategory(Base):
    __tablename__ = "idea_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey("idea_categories.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    children = relationship("IdeaCategory", back_populates="parent")
    parent = relationship("IdeaCategory", back_populates="children", remote_side=[id])
    summaries = relationship("ConversationSummary", secondary=summary_categories, back_populates="categories")

class IdeaTag(Base):
    __tablename__ = "idea_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    summaries = relationship("ConversationSummary", secondary=summary_tags, back_populates="tags")

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()