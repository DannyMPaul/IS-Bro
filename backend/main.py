from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session

# Load environment variables
load_dotenv()

from ai_service import AIService
from models import (
    ChatMessage, IdeaProposal, ConversationState,
    UserCreate, UserLogin, UserResponse, JWTToken,
    MultiPerspectiveRequest, MultiPerspectiveResponse, AIResponse,
    MarketResearchRequest, MarketResearchResponse, CompetitorData, IndustryData, MarketTrendData,
    IdeaMapRequest, IdeaMapResponse, IdeaNodeData, IdeaEdgeData,
    AnalyticsRequest, AnalyticsDashboardResponse, ConversationAnalyticsData, UserAnalyticsData, IdeaAnalyticsData, SystemAnalyticsData,
    ConversationTemplateResponse, TemplateSearchRequest, StartFromTemplateRequest,
    ConversationSearchRequest, ConversationSearchResponse, ConversationSearchResult,
    SummaryType, SummaryRequest, ConversationSummaryResponse, ConversationSummaryList
)
from database import create_tables, get_db, Conversation as DBConversation, Message as DBMessage, User as DBUser
from chat_service import ChatService
from auth_service import AuthService
from multi_ai_service import MultiAIService, AIPersona, AIProvider
from market_research_service import MarketResearchService
from visual_mapping_service import VisualMappingService
from analytics_service import AnalyticsService
from template_service import TemplateService, template_to_dict
from search_service import SearchService
from summary_service import SummaryService

security = HTTPBearer(auto_error=False)

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
multi_ai_service = MultiAIService()
market_research_service = MarketResearchService()
visual_mapping_service = VisualMappingService()
analytics_service = AnalyticsService()
template_service = TemplateService()
search_service = SearchService()
conversations = {}  # Backward compatibility

# Authentication dependency
async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security), db: Session = Depends(get_db)) -> DBUser:
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    auth_service = AuthService(db)
    email = auth_service.verify_token(credentials.credentials)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = auth_service.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

# Optional auth dependency for guest access
async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security), db: Session = Depends(get_db)) -> Optional[DBUser]:
    if not credentials or not credentials.credentials:
        return None
    
    auth_service = AuthService(db)
    email = auth_service.verify_token(credentials.credentials)
    if not email:
        return None
    
    return auth_service.get_user_by_email(email)

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    conversation_state: str
    suggestions: Optional[List[str]] = None
    user_message_timestamp: str
    assistant_message_timestamp: str

@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db), current_user: Optional[DBUser] = Depends(get_current_user_optional)):
    try:
        if not request.session_id:
            request.session_id = f"session_{datetime.now().timestamp()}"
        
        chat_service = ChatService(db)
        
        # Get or create conversation in database
        conversation_db = chat_service.get_conversation(request.session_id)
        if not conversation_db:
            # Associate conversation with user if authenticated
            user_id = current_user.id if current_user else None
            conversation_db = chat_service.create_conversation(request.session_id, user_id=user_id)
        
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
        user_msg = chat_service.add_message(request.session_id, "user", request.message)
        assistant_msg = chat_service.add_message(request.session_id, "assistant", response.message, response.suggestions)
        
        return ChatResponse(
            response=response.message,
            session_id=request.session_id,
            conversation_state=conversation.current_stage.value,
            suggestions=response.suggestions,
            user_message_timestamp=user_msg.timestamp.isoformat() + 'Z',
            assistant_message_timestamp=assistant_msg.timestamp.isoformat() + 'Z'
        )
    
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversations")
def get_conversations(db: Session = Depends(get_db), current_user: Optional[DBUser] = Depends(get_current_user_optional)):
    chat_service = ChatService(db)
    
    # If authenticated, get user's conversations; otherwise get all conversations (guest mode)
    if current_user:
        conversations_db = chat_service.get_user_conversations(current_user.id)
    else:
        conversations_db = chat_service.get_all_conversations()
    
    return [{
        "id": conv.id,
        "title": conv.title,
        "created_at": conv.created_at.isoformat() + 'Z' if conv.created_at else None,
        "updated_at": conv.updated_at.isoformat() + 'Z' if conv.updated_at else None,
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
        "timestamp": msg.timestamp.isoformat() + 'Z' if msg.timestamp else None,
        "suggestions": json.loads(msg.suggestions) if msg.suggestions else None
    } for msg in conversation.messages]
    
    return {
        "id": conversation.id,
        "title": conversation.title,
        "stage": conversation.stage,
        "messages": messages,
        "created_at": conversation.created_at.isoformat() + 'Z' if conversation.created_at else None,
        "updated_at": conversation.updated_at.isoformat() + 'Z' if conversation.updated_at else None
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

@app.get("/api/conversation/{session_id}/insights")
def get_conversation_insights(session_id: str, db: Session = Depends(get_db)):
    """Get insights and follow-up questions for a conversation"""
    try:
        if session_id not in conversations:
            # Try to load from database
            chat_service = ChatService(db)
            conversation_db = chat_service.get_conversation(session_id)
            if not conversation_db:
                raise HTTPException(status_code=404, detail="Conversation not found")
            
            # Convert to in-memory format
            conversation = ConversationState()
            conversation.id = session_id
            for msg in conversation_db.messages:
                conversation.add_message(msg.role, msg.content)
            conversations[session_id] = conversation
        
        conversation = conversations[session_id]
        insights = ai_service.get_conversation_insights(conversation)
        
        return insights
        
    except Exception as e:
        print(f"Error getting conversation insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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

# Summary endpoints
@app.post("/api/summaries", response_model=ConversationSummaryResponse)
async def create_conversation_summary(
    request: SummaryRequest,
    db: Session = Depends(get_db),
    current_user: Optional[DBUser] = Depends(get_current_user_optional)
):
    """Generate a new summary for a conversation"""
    try:
        summary_service = SummaryService(db)
        return await summary_service.generate_summary(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/summaries/{summary_id}", response_model=ConversationSummaryResponse)
async def get_summary(
    summary_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[DBUser] = Depends(get_current_user_optional)
):
    """Get a specific summary by ID"""
    try:
        summary_service = SummaryService(db)
        return await summary_service.get_summary(summary_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversations/{conversation_id}/summaries", response_model=ConversationSummaryList)
async def get_conversation_summaries(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[DBUser] = Depends(get_current_user_optional)
):
    """Get all summaries for a conversation"""
    try:
        summary_service = SummaryService(db)
        summaries = await summary_service.get_conversation_summaries(conversation_id)
        return ConversationSummaryList(summaries=summaries)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Authentication endpoints
@app.post("/api/auth/register", response_model=UserResponse)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = db.query(DBUser).filter(DBUser.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        auth_service = AuthService(db)
        user = auth_service.create_user(user_data, db)
        
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            created_at=user.created_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

@app.post("/api/auth/login", response_model=JWTToken)
def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    try:
        auth_service = AuthService(db)
        user = auth_service.authenticate_user(user_credentials.email, user_credentials.password, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token = auth_service.create_access_token({"sub": user.email})
        
        return JWTToken(
            access_token=access_token,
            token_type="bearer"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@app.get("/api/auth/me", response_model=UserResponse)
def get_current_user_info(current_user: DBUser = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        created_at=current_user.created_at
    )

# Multi-AI endpoints
@app.get("/api/ai/providers")
def get_available_providers():
    """Get list of available AI providers"""
    return {
        "providers": [provider.value for provider in multi_ai_service.get_available_providers()],
        "personas": [persona.value for persona in AIPersona]
    }

@app.post("/api/chat/multi-perspective", response_model=MultiPerspectiveResponse)
def chat_multi_perspective(request: MultiPerspectiveRequest, db: Session = Depends(get_db), current_user: Optional[DBUser] = Depends(get_current_user_optional)):
    """Get multi-perspective AI analysis for an idea"""
    try:
        if not request.session_id:
            request.session_id = f"session_{datetime.now().timestamp()}"
        
        chat_service = ChatService(db)
        
        # Get or create conversation in database
        conversation_db = chat_service.get_conversation(request.session_id)
        if not conversation_db:
            user_id = current_user.id if current_user else None
            conversation_db = chat_service.create_conversation(request.session_id, user_id=user_id)
        
        # Get conversation history for context
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in conversation_db.messages[-10:]  # Last 10 messages
        ]
        
        # Save user message first
        user_msg = chat_service.add_message(request.session_id, "user", request.message)
        
        # Get multi-perspective analysis
        perspectives = multi_ai_service.get_multi_perspective_analysis(
            request.message, 
            conversation_history
        )
        
        # Convert to AIResponse objects
        ai_responses = []
        assistant_timestamps = []
        for perspective in perspectives:
            ai_response = AIResponse(
                message=perspective["response"],
                provider=perspective.get("provider"),
                persona=perspective.get("persona"),
                model=perspective.get("model")
            )
            ai_responses.append(ai_response)
            
            # Save each perspective as a separate assistant message
            assistant_msg = chat_service.add_message(
                request.session_id, 
                "assistant", 
                f"[{perspective.get('persona', 'AI')}]: {perspective['response']}"
            )
            assistant_timestamps.append(assistant_msg.timestamp.isoformat())
        
        return MultiPerspectiveResponse(
            perspectives=ai_responses,
            session_id=request.session_id,
            conversation_state="exploring",
            user_message_timestamp=user_msg.timestamp.isoformat() + 'Z',
            assistant_message_timestamps=[ts.isoformat() + 'Z' for ts in assistant_timestamps]
        )
    
    except Exception as e:
        print(f"Error in multi-perspective chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/persona")
def chat_with_persona(
    request: dict,
    db: Session = Depends(get_db),
    current_user: Optional[DBUser] = Depends(get_current_user_optional)
):
    """Chat with a specific AI persona"""
    try:
        message = request.get("message")
        persona = request.get("persona", AIPersona.SOCRATIC_MENTOR.value)
        provider = request.get("provider", AIProvider.GEMINI.value)
        session_id = request.get("session_id")
        
        if not session_id:
            session_id = f"session_{datetime.now().timestamp()}"
        
        chat_service = ChatService(db)
        
        # Get or create conversation
        conversation_db = chat_service.get_conversation(session_id)
        if not conversation_db:
            user_id = current_user.id if current_user else None
            conversation_db = chat_service.create_conversation(session_id, user_id=user_id)
        
        # Get conversation history
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in conversation_db.messages[-10:]
        ]
        
        # Get AI response with specific persona
        ai_response = multi_ai_service.get_response(
            message,
            AIPersona(persona),
            AIProvider(provider),
            conversation_history
        )
        
        # Save messages to database
        chat_service.add_message(session_id, "user", message)
        chat_service.add_message(
            session_id, 
            "assistant", 
            ai_response["response"],
            None
        )
        
        return {
            "response": ai_response["response"],
            "session_id": session_id,
            "persona": ai_response.get("persona"),
            "provider": ai_response.get("provider"),
            "model": ai_response.get("model")
        }
    
    except Exception as e:
        print(f"Error in persona chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Market Research endpoints
@app.post("/api/market-research", response_model=MarketResearchResponse)
async def conduct_market_research(
    request: MarketResearchRequest,
    db: Session = Depends(get_db),
    current_user: Optional[DBUser] = Depends(get_current_user_optional)
):
    """Conduct comprehensive market research for an idea"""
    try:
        # Conduct market research
        research_report = await market_research_service.conduct_market_research(
            request.idea, 
            request.industry
        )
        
        # Convert to response format
        competitors_data = [
            CompetitorData(
                name=comp.name,
                description=comp.description,
                funding=comp.funding,
                market_share=comp.market_share,
                key_features=comp.key_features,
                url=comp.url
            ) for comp in research_report.competitors
        ]
        
        industry_data = IndustryData(
            industry=research_report.industry_insights.industry,
            market_size=research_report.industry_insights.market_size,
            growth_rate=research_report.industry_insights.growth_rate,
            key_trends=research_report.industry_insights.key_trends,
            challenges=research_report.industry_insights.challenges,
            opportunities=research_report.industry_insights.opportunities
        )
        
        trends_data = [
            MarketTrendData(
                keyword=trend.keyword,
                interest_score=trend.interest_score,
                growth_rate=trend.growth_rate,
                related_topics=trend.related_topics,
                time_period=trend.time_period
            ) for trend in research_report.market_trends
        ]
        
        # Save research to conversation if session_id provided
        if request.session_id:
            chat_service = ChatService(db)
            conversation_db = chat_service.get_conversation(request.session_id)
            if conversation_db:
                research_summary = f"Market Research for: {request.idea}\n\n"
                research_summary += f"Industry: {industry_data.industry} (${industry_data.market_size})\n"
                research_summary += f"Growth Rate: {industry_data.growth_rate}%\n"
                research_summary += f"Key Competitors: {', '.join([c.name for c in competitors_data[:3]])}\n"
                research_summary += f"Top Recommendations: {'; '.join(research_report.recommendations[:2])}"
                
                chat_service.add_message(
                    request.session_id,
                    "system",
                    research_summary
                )
        
        return MarketResearchResponse(
            query=research_report.query,
            industry_insights=industry_data,
            competitors=competitors_data,
            market_trends=trends_data,
            news_headlines=research_report.news_headlines,
            recommendations=research_report.recommendations,
            research_timestamp=research_report.research_timestamp
        )
    
    except Exception as e:
        print(f"Error conducting market research: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Visual Mapping endpoints
@app.post("/api/idea-map", response_model=IdeaMapResponse)
async def create_idea_map(
    request: IdeaMapRequest,
    db: Session = Depends(get_db),
    current_user: Optional[DBUser] = Depends(get_current_user_optional)
):
    """Create a visual idea map from conversation data"""
    try:
        # Get conversation messages for context
        conversation_messages = []
        market_data = None
        
        if request.session_id:
            chat_service = ChatService(db)
            conversation_db = chat_service.get_conversation(request.session_id)
            if conversation_db:
                conversation_messages = [
                    {"role": msg.role, "content": msg.content}
                    for msg in conversation_db.messages
                ]
                
                # Get market research data if requested
                if request.include_market_data:
                    try:
                        research_report = await market_research_service.conduct_market_research(
                            request.central_idea
                        )
                        market_data = {
                            "competitors": [
                                {"name": c.name, "description": c.description}
                                for c in research_report.competitors
                            ],
                            "industry_insights": {
                                "opportunities": research_report.industry_insights.opportunities
                            }
                        }
                    except Exception as e:
                        print(f"Failed to get market data for mapping: {e}")
        
        # Create the idea map
        idea_map = visual_mapping_service.create_idea_map(
            request.central_idea,
            conversation_messages,
            market_data
        )
        
        # Convert to response format
        nodes_data = [
            IdeaNodeData(
                id=node.id,
                label=node.label,
                type=node.type.value,
                description=node.description,
                importance=node.importance,
                feasibility=node.feasibility,
                x=node.x,
                y=node.y,
                color=node.color,
                size=node.size
            ) for node in idea_map.nodes
        ]
        
        edges_data = [
            IdeaEdgeData(
                source=edge.source,
                target=edge.target,
                type=edge.type.value,
                weight=edge.weight,
                description=edge.description
            ) for edge in idea_map.edges
        ]
        
        return IdeaMapResponse(
            central_idea=idea_map.central_idea,
            nodes=nodes_data,
            edges=edges_data,
            clusters=idea_map.clusters,
            created_at=idea_map.created_at,
            updated_at=idea_map.updated_at
        )
    
    except Exception as e:
        print(f"Error creating idea map: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Template endpoints
@app.get("/api/templates", response_model=List[ConversationTemplateResponse])
def get_conversation_templates(
    category: Optional[str] = None,
    current_user: Optional[DBUser] = Depends(get_current_user_optional)
):
    """Get available conversation templates"""
    try:
        if category:
            from template_service import TemplateCategory
            templates = template_service.get_templates_by_category(TemplateCategory(category))
        else:
            templates = template_service.get_all_templates()
        
        return [ConversationTemplateResponse(**template_to_dict(t)) for t in templates]
    
    except Exception as e:
        print(f"Error getting templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/templates/search", response_model=List[ConversationTemplateResponse])
def search_templates(
    request: TemplateSearchRequest,
    current_user: Optional[DBUser] = Depends(get_current_user_optional)
):
    """Search conversation templates"""
    try:
        if request.query:
            templates = template_service.search_templates(request.query)
        elif request.category:
            from template_service import TemplateCategory
            templates = template_service.get_templates_by_category(TemplateCategory(request.category))
        else:
            templates = template_service.get_all_templates()
        
        return [ConversationTemplateResponse(**template_to_dict(t)) for t in templates]
    
    except Exception as e:
        print(f"Error searching templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/templates/categories")
def get_template_categories(
    current_user: Optional[DBUser] = Depends(get_current_user_optional)
):
    """Get available template categories"""
    try:
        categories = template_service.get_categories()
        return {"categories": categories}
    
    except Exception as e:
        print(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/templates/start")
def start_conversation_from_template(
    request: StartFromTemplateRequest,
    db: Session = Depends(get_db),
    current_user: Optional[DBUser] = Depends(get_current_user_optional)
):
    """Start a new conversation from a template"""
    try:
        template = template_service.get_template_by_id(request.template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        # Create new conversation
        session_id = request.session_id or f"session_{datetime.now().timestamp()}"
        chat_service = ChatService(db)
        
        user_id = current_user.id if current_user else None
        conversation_db = chat_service.create_conversation(
            session_id, 
            title=template.title,
            user_id=user_id
        )
        
        # Add template initial message
        chat_service.add_message(session_id, "user", template.initial_prompt)
        
        # Get AI response to the template prompt
        conversation = ConversationState()
        conversation.id = session_id
        conversation.add_user_message(template.initial_prompt)
        
        ai_response = ai_service.process_message(template.initial_prompt, conversation)
        
        # Add AI response with template suggestions
        suggestions = template.suggested_questions[:3]  # Limit to 3 suggestions
        chat_service.add_message(session_id, "assistant", ai_response.message, suggestions)
        
        return {
            "session_id": session_id,
            "template_id": template.id,
            "template_title": template.title,
            "initial_prompt": template.initial_prompt,
            "ai_response": ai_response.message,
            "suggestions": suggestions
        }
    
    except Exception as e:
        print(f"Error starting conversation from template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Search endpoints
@app.post("/api/search/conversations", response_model=ConversationSearchResponse)
def search_conversations(
    request: ConversationSearchRequest,
    db: Session = Depends(get_db),
    current_user: Optional[DBUser] = Depends(get_current_user_optional)
):
    """Search through conversations"""
    try:
        user_id = current_user.id if current_user else None
        
        search_results = search_service.search_conversations(
            db=db,
            query=request.query,
            user_id=user_id,
            filters=request.filters,
            limit=request.limit
        )
        
        return ConversationSearchResponse(**search_results)
    
    except Exception as e:
        print(f"Error searching conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search/suggestions")
def get_search_suggestions(
    q: str,
    db: Session = Depends(get_db),
    current_user: Optional[DBUser] = Depends(get_current_user_optional)
):
    """Get search suggestions"""
    try:
        user_id = current_user.id if current_user else None
        suggestions = search_service.get_search_suggestions(db, q, user_id)
        return {"suggestions": suggestions}
    
    except Exception as e:
        print(f"Error getting search suggestions: {e}")
        return {"suggestions": []}

@app.get("/api/search/filters")
def get_search_filters(
    db: Session = Depends(get_db),
    current_user: Optional[DBUser] = Depends(get_current_user_optional)
):
    """Get available search filter options"""
    try:
        user_id = current_user.id if current_user else None
        filters = search_service.get_filter_options(db, user_id)
        return filters
    
    except Exception as e:
        print(f"Error getting search filters: {e}")
        return {"stages": [], "date_ranges": []}

# Analytics endpoints
@app.post("/api/analytics", response_model=AnalyticsDashboardResponse)
def get_analytics_dashboard(
    request: AnalyticsRequest,
    db: Session = Depends(get_db),
    current_user: Optional[DBUser] = Depends(get_current_user_optional)
):
    """Get comprehensive analytics dashboard"""
    try:
        user_id = current_user.id if (request.user_specific and current_user) else None
        
        dashboard = analytics_service.generate_dashboard(db, user_id)
        
        return AnalyticsDashboardResponse(
            conversation_analytics=ConversationAnalyticsData(
                total_conversations=dashboard.conversation_analytics.total_conversations,
                active_conversations=dashboard.conversation_analytics.active_conversations,
                average_length=dashboard.conversation_analytics.average_length,
                completion_rate=dashboard.conversation_analytics.completion_rate,
                stage_distribution=dashboard.conversation_analytics.stage_distribution,
                user_engagement=dashboard.conversation_analytics.user_engagement
            ),
            user_analytics=UserAnalyticsData(
                total_users=dashboard.user_analytics.total_users,
                active_users=dashboard.user_analytics.active_users,
                retention_rate=dashboard.user_analytics.retention_rate,
                average_session_length=dashboard.user_analytics.average_session_length,
                feature_usage=dashboard.user_analytics.feature_usage,
                user_journey=dashboard.user_analytics.user_journey
            ),
            idea_analytics=IdeaAnalyticsData(
                total_ideas=dashboard.idea_analytics.total_ideas,
                category_distribution=dashboard.idea_analytics.category_distribution,
                success_metrics=dashboard.idea_analytics.success_metrics,
                trending_concepts=dashboard.idea_analytics.trending_concepts,
                ai_persona_effectiveness=dashboard.idea_analytics.ai_persona_effectiveness
            ),
            system_analytics=SystemAnalyticsData(
                api_usage=dashboard.system_analytics.api_usage,
                response_times=dashboard.system_analytics.response_times,
                error_rates=dashboard.system_analytics.error_rates,
                popular_features=dashboard.system_analytics.popular_features,
                growth_metrics=dashboard.system_analytics.growth_metrics
            ),
            generated_at=dashboard.generated_at
        )
    
    except Exception as e:
        print(f"Error generating analytics dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/conversation/{conversation_id}")
def get_conversation_insights(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[DBUser] = Depends(get_current_user_optional)
):
    """Get detailed insights for a specific conversation"""
    try:
        insights = analytics_service.get_conversation_insights(db, conversation_id)
        return insights
    
    except Exception as e:
        print(f"Error getting conversation insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
