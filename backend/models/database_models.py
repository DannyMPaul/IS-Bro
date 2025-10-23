from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Table, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

# Association tables for many-to-many relationships
idea_category_association = Table(
    'idea_category_association',
    Base.metadata,
    Column('idea_id', String, ForeignKey('conversations.id')),
    Column('category_id', Integer, ForeignKey('idea_categories.id'))
)

idea_tag_association = Table(
    'idea_tag_association',
    Base.metadata,
    Column('idea_id', String, ForeignKey('conversations.id')),
    Column('tag_id', Integer, ForeignKey('idea_tags.id'))
)

idea_relationships = Table(
    'idea_relationships',
    Base.metadata,
    Column('source_id', String, ForeignKey('conversations.id')),
    Column('target_id', String, ForeignKey('conversations.id')),
    Column('relationship_type', String),
    Column('created_at', DateTime, default=datetime.utcnow)
)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    conversations = relationship("Conversation", back_populates="user")

class Conversation(Base):
    __tablename__ = 'conversations'

    id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String)
    stage = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")
    summary = relationship("ConversationSummary", back_populates="conversation", uselist=False)
    categories = relationship("IdeaCategory", secondary=idea_category_association, back_populates="ideas")
    tags = relationship("IdeaTag", secondary=idea_tag_association, back_populates="ideas")
    
    # For idea relationship mapping
    related_to = relationship(
        "Conversation",
        secondary=idea_relationships,
        primaryjoin=id==idea_relationships.c.source_id,
        secondaryjoin=id==idea_relationships.c.target_id,
        backref="related_from"
    )

class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String, ForeignKey('conversations.id'))
    role = Column(String)  # 'user' or 'assistant'
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    provider = Column(String, nullable=True)  # AI provider (e.g., 'gemini', 'openai')
    persona = Column(String, nullable=True)  # AI persona used
    suggestions = Column(String, nullable=True)  # JSON string of suggested responses

    conversation = relationship("Conversation", back_populates="messages")

class ConversationSummary(Base):
    __tablename__ = 'conversation_summaries'

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String, ForeignKey('conversations.id'), unique=True)
    content = Column(String)  # Markdown formatted summary
    completion_percentage = Column(Integer, default=0)  # 0-100
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    conversation = relationship("Conversation", back_populates="summary")

class IdeaCategory(Base):
    __tablename__ = 'idea_categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(String, nullable=True)
    color = Column(String, nullable=True)  # Hex color code for UI
    created_at = Column(DateTime, default=datetime.utcnow)
    
    ideas = relationship("Conversation", secondary=idea_category_association, back_populates="categories")

class IdeaTag(Base):
    __tablename__ = 'idea_tags'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    ideas = relationship("Conversation", secondary=idea_tag_association, back_populates="tags")