from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session

# Load environment variables
load_dotenv()

from ai_service import AIService
from models import ChatMessage, IdeaProposal, ConversationState
from database import create_tables, get_db, Conversation as DBConversation, Message as DBMessage
from chat_service import ChatService

app = FastAPI(title="Idea Shaper API", version="2.0.0")

# Create database tables
create_tables()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ai_service = AIService()
conversations = {}  # Backward compatibility

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    conversation_state: str
    suggestions: Optional[List[str]] = None

@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        if not request.session_id:
            request.session_id = f"session_{datetime.now().timestamp()}"
        
        chat_service = ChatService(db)
        
        # Get or create conversation in database
        conversation_db = chat_service.get_conversation(request.session_id)
        if not conversation_db:
            conversation_db = chat_service.create_conversation(request.session_id)
        
        # Convert to in-memory format for AI processing (backward compatibility)
        if request.session_id not in conversations:
            conversation = ConversationState()
            conversation.id = request.session_id
            # Load existing messages from DB
            for msg in conversation_db.messages:
                conversation.messages.append(ChatMessage(
                    role=msg.role,
                    content=msg.content,
                    timestamp=msg.timestamp,
                    suggestions=json.loads(msg.suggestions) if msg.suggestions else None
                ))
            conversations[request.session_id] = conversation
        
        conversation = conversations[request.session_id]
        
        # Process with AI
        response = ai_service.process_message(request.message, conversation)
        
        # Save to database
        chat_service.add_message(request.session_id, "user", request.message)
        chat_service.add_message(request.session_id, "assistant", response.message, response.suggestions)
        
        return ChatResponse(
            response=response.message,
            session_id=request.session_id,
            conversation_state=conversation.current_stage.value,
            suggestions=response.suggestions
        )
    
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversations")
def get_conversations(db: Session = Depends(get_db)):
    chat_service = ChatService(db)
    conversations_db = chat_service.get_all_conversations()
    
    return [{
        "id": conv.id,
        "title": conv.title,
        "created_at": conv.created_at,
        "updated_at": conv.updated_at,
        "stage": conv.stage,
        "message_count": len(conv.messages)
    } for conv in conversations_db]

@app.get("/api/conversations/{conversation_id}")
def get_conversation_detail(conversation_id: str, db: Session = Depends(get_db)):
    chat_service = ChatService(db)
    conversation = chat_service.get_conversation(conversation_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = [{
        "role": msg.role,
        "content": msg.content,
        "timestamp": msg.timestamp,
        "suggestions": json.loads(msg.suggestions) if msg.suggestions else None
    } for msg in conversation.messages]
    
    return {
        "id": conversation.id,
        "title": conversation.title,
        "stage": conversation.stage,
        "messages": messages,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at
    }

@app.put("/api/conversations/{conversation_id}/title")
def update_conversation_title(conversation_id: str, title: str, db: Session = Depends(get_db)):
    chat_service = ChatService(db)
    chat_service.update_conversation_title(conversation_id, title)
    return {"message": "Title updated successfully"}

@app.delete("/api/conversations/{conversation_id}")
def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    chat_service = ChatService(db)
    chat_service.delete_conversation(conversation_id)
    
    # Remove from in-memory storage too
    if conversation_id in conversations:
        del conversations[conversation_id]
    
    return {"message": "Conversation deleted successfully"}

@app.get("/api/conversation/{session_id}")
def get_conversation(session_id: str):
    if session_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation = conversations[session_id]
    return {
        "messages": conversation.messages,
        "stage": conversation.current_stage.value,
        "current_idea": conversation.current_idea
    }

@app.post("/api/proposal/{session_id}")
def generate_proposal(session_id: str):
    if session_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation = conversations[session_id]
    proposal = ai_service.generate_proposal(conversation)
    
    return proposal

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
