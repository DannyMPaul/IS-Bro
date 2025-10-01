from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ConversationStage(str, Enum):
    INITIAL = "initial"
    EXPLORING = "exploring"
    STRUCTURING = "structuring"
    ALTERNATIVES = "alternatives"
    REFINEMENT = "refinement"
    PROPOSAL = "proposal"

# Auth Models
class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class JWTToken(BaseModel):
    access_token: str
    token_type: str

# Chat Models
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
    message: str
    suggestions: Optional[List[str]] = None
    conversation_id: Optional[str] = None
    stage: ConversationStage = ConversationStage.INITIAL
    provider: Optional[str] = None
    persona: Optional[str] = None
    model: Optional[str] = None

class MultiPerspectiveRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    enable_multi_perspective: bool = False

class MultiPerspectiveResponse(BaseModel):
    perspectives: List[AIResponse]
    session_id: str
    conversation_state: str
    user_message_timestamp: str
    assistant_message_timestamps: List[str]

# Market Research Models
class MarketResearchRequest(BaseModel):
    idea: str
    industry: Optional[str] = None
    session_id: Optional[str] = None

class CompetitorData(BaseModel):
    name: str
    description: str
    funding: Optional[str] = None
    market_share: Optional[float] = None
    key_features: List[str]
    url: Optional[str] = None

class IndustryData(BaseModel):
    industry: str
    market_size: Optional[str] = None
    growth_rate: Optional[float] = None
    key_trends: List[str]
    challenges: List[str]
    opportunities: List[str]

class MarketTrendData(BaseModel):
    keyword: str
    interest_score: float
    growth_rate: float
    related_topics: List[str]
    time_period: str

class MarketResearchResponse(BaseModel):
    query: str
    industry_insights: IndustryData
    competitors: List[CompetitorData]
    market_trends: List[MarketTrendData]
    news_headlines: List[str]
    recommendations: List[str]
    research_timestamp: str

# Visual Mapping Models
class IdeaMapRequest(BaseModel):
    central_idea: str
    session_id: Optional[str] = None
    include_market_data: bool = False

class IdeaNodeData(BaseModel):
    id: str
    label: str
    type: str
    description: str
    importance: float
    feasibility: float
    x: Optional[float] = None
    y: Optional[float] = None
    color: Optional[str] = None
    size: Optional[float] = None

class IdeaEdgeData(BaseModel):
    source: str
    target: str
    type: str
    weight: float
    description: Optional[str] = None

class IdeaMapResponse(BaseModel):
    central_idea: str
    nodes: List[IdeaNodeData]
    edges: List[IdeaEdgeData]
    clusters: Dict[str, List[str]]
    created_at: str
    updated_at: str

# Analytics Models
class AnalyticsRequest(BaseModel):
    user_specific: bool = False
    time_range: Optional[str] = "30d"  # 7d, 30d, 90d, 1y

class ConversationAnalyticsData(BaseModel):
    total_conversations: int
    active_conversations: int
    average_length: float
    completion_rate: float
    stage_distribution: Dict[str, int]
    user_engagement: Dict[str, float]

class UserAnalyticsData(BaseModel):
    total_users: int
    active_users: int
    retention_rate: float
    average_session_length: float
    feature_usage: Dict[str, int]
    user_journey: List[Dict[str, Any]]

class IdeaAnalyticsData(BaseModel):
    total_ideas: int
    category_distribution: Dict[str, int]
    success_metrics: Dict[str, float]
    trending_concepts: List[str]
    ai_persona_effectiveness: Dict[str, float]

class SystemAnalyticsData(BaseModel):
    api_usage: Dict[str, int]
    response_times: Dict[str, float]
    error_rates: Dict[str, float]
    popular_features: List[str]
    growth_metrics: Dict[str, float]

class AnalyticsDashboardResponse(BaseModel):
    conversation_analytics: ConversationAnalyticsData
    user_analytics: UserAnalyticsData
    idea_analytics: IdeaAnalyticsData
    system_analytics: SystemAnalyticsData
    generated_at: str

class ConversationState(BaseModel):
    id: Optional[str] = None
    messages: List[ChatMessage] = []
    current_stage: ConversationStage = ConversationStage.INITIAL
    current_idea: IdeaStructure = IdeaStructure()
    interaction_count: int = 0
    last_updated: datetime = datetime.now()
    
    def add_user_message(self, content: str):
        message = ChatMessage(
            role="user",
            content=content,
            timestamp=datetime.now()
        )
        self.messages.append(message)
        self.interaction_count += 1
    
    def add_ai_message(self, content: str, suggestions: Optional[List[str]] = None):
        message = ChatMessage(
            role="assistant",
            content=content,
            timestamp=datetime.now(),
            suggestions=suggestions
        )
        self.messages.append(message)
    
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
        current_index = stages.index(self.current_stage)
        if current_index < len(stages) - 1:
            self.current_stage = stages[current_index + 1]
