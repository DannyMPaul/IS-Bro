from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class ConversationStage(str, Enum):
    INITIAL = "initial"
    EXPLORING = "exploring"
    STRUCTURING = "structuring"
    ALTERNATIVES = "alternatives"
    REFINEMENT = "refinement"
    PROPOSAL = "proposal"

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime
    suggestions: Optional[List[str]] = None

class IdeaStructure(BaseModel):
    problem: Optional[str] = None
    audience: Optional[str] = None
    solution: Optional[str] = None
    impact: Optional[str] = None
    constraints: Optional[str] = None

class IdeaProposal(BaseModel):
    title: str
    summary: str
    problem: str
    solution: str
    features: List[str]
    tech_stack: List[str]
    next_steps: List[str]
    created_at: datetime

class AIResponse(BaseModel):
    content: str
    suggestions: Optional[List[str]] = None
    should_advance_stage: bool = False

class ConversationState(BaseModel):
    session_id: Optional[str] = None
    messages: List[ChatMessage] = []
    stage: ConversationStage = ConversationStage.INITIAL
    current_idea: IdeaStructure = IdeaStructure()
    interaction_count: int = 0
    
    def add_message(self, role: str, content: str, suggestions: Optional[List[str]] = None):
        message = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.now(),
            suggestions=suggestions
        )
        self.messages.append(message)
        self.interaction_count += 1
    
    def advance_stage(self):
        stages = list(ConversationStage)
        current_index = stages.index(self.stage)
        if current_index < len(stages) - 1:
            self.stage = stages[current_index + 1]
