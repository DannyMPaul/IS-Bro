from sqlalchemy.orm import Session
from database import Conversation, Message, get_db
from datetime import datetime
import json
import re

class ChatService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_conversation(self, conversation_id: str, title: str = None, user_id: int = None) -> Conversation:
        conversation = Conversation(
            id=conversation_id,
            title=title or "New Chat",
            user_id=user_id
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation
    
    def get_conversation(self, conversation_id: str) -> Conversation:
        return self.db.query(Conversation).filter(Conversation.id == conversation_id).first()
    
    def get_all_conversations(self) -> list[Conversation]:
        return self.db.query(Conversation).order_by(Conversation.updated_at.desc()).all()
    
    def get_user_conversations(self, user_id: int) -> list[Conversation]:
        """Get all conversations for a specific user"""
        return self.db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(Conversation.updated_at.desc()).all()
    
    def update_conversation_title(self, conversation_id: str, title: str):
        conversation = self.get_conversation(conversation_id)
        if conversation:
            conversation.title = title
            conversation.updated_at = datetime.utcnow()
            self.db.commit()
    
    def delete_conversation(self, conversation_id: str):
        conversation = self.get_conversation(conversation_id)
        if conversation:
            self.db.delete(conversation)
            self.db.commit()
    
    def add_message(self, conversation_id: str, role: str, content: str, suggestions: list = None):
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            suggestions=json.dumps(suggestions) if suggestions else None
        )
        self.db.add(message)
        
        # Update conversation timestamp
        conversation = self.get_conversation(conversation_id)
        if conversation:
            conversation.updated_at = datetime.utcnow()
            
            # Auto-generate title from first user message
            if conversation.title == "New Chat" and role == "user":
                conversation.title = self.generate_title_from_message(content)
        
        self.db.commit()
        self.db.refresh(message)
        return message
    
    def generate_title_from_message(self, message: str) -> str:
        # Clean and truncate message for title
        clean_message = re.sub(r'[^\w\s]', '', message)
        words = clean_message.split()[:5]  # First 5 words
        title = ' '.join(words)
        return title.capitalize() if title else "New Chat"