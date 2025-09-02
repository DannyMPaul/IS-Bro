from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from ai_service import AIService
from models import ChatMessage, IdeaProposal, ConversationState

app = FastAPI(title="Idea Shaper API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ai_service = AIService()
conversations = {}

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    conversation_state: str
    suggestions: Optional[List[str]] = None

@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        if not request.session_id:
            request.session_id = f"session_{datetime.now().timestamp()}"
        
        if request.session_id not in conversations:
            conversation = ConversationState()
            conversation.id = request.session_id
            conversations[request.session_id] = conversation
        
        conversation = conversations[request.session_id]
        
        response = ai_service.process_message(
            request.message, 
            conversation
        )
        
        return ChatResponse(
            response=response.message,
            session_id=request.session_id,
            conversation_state=conversation.current_stage.value,
            suggestions=response.suggestions
        )
    
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
