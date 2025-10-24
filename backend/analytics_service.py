from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import Conversation, Message, User
import json

@dataclass
class ConversationAnalytics:
    total_conversations: int
    active_conversations: int
    average_length: float
    completion_rate: float
    stage_distribution: Dict[str, int]
    user_engagement: Dict[str, float]

@dataclass
class UserAnalytics:
    total_users: int
    active_users: int
    retention_rate: float
    average_session_length: float
    feature_usage: Dict[str, int]
    user_journey: List[Dict[str, Any]]

@dataclass
class IdeaAnalytics:
    total_ideas: int
    category_distribution: Dict[str, int]
    success_metrics: Dict[str, float]
    trending_concepts: List[str]
    ai_persona_effectiveness: Dict[str, float]

@dataclass
class SystemAnalytics:
    api_usage: Dict[str, int]
    response_times: Dict[str, float]
    error_rates: Dict[str, float]
    popular_features: List[str]
    growth_metrics: Dict[str, float]

@dataclass
class AnalyticsDashboard:
    conversation_analytics: ConversationAnalytics
    user_analytics: UserAnalytics
    idea_analytics: IdeaAnalytics
    system_analytics: SystemAnalytics
    generated_at: str

class AnalyticsService:
    def __init__(self):
        print("Analytics Service initialized")
    
    def generate_dashboard(self, db: Session, user_id: Optional[int] = None) -> AnalyticsDashboard:
        try:
            # Generate analytics for different aspects
            conversation_analytics = self._analyze_conversations(db, user_id)
            user_analytics = self._analyze_users(db)
            idea_analytics = self._analyze_ideas(db, user_id)
            system_analytics = self._analyze_system_performance(db)
            
            return AnalyticsDashboard(
                conversation_analytics=conversation_analytics,
                user_analytics=user_analytics,
                idea_analytics=idea_analytics,
                system_analytics=system_analytics,
                generated_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            print(f"Error generating analytics dashboard: {e}")
            return self._get_mock_analytics()
    
    def _analyze_conversations(self, db: Session, user_id: Optional[int] = None) -> ConversationAnalytics:
        try:
            # Base query
            base_query = db.query(Conversation)
            if user_id:
                base_query = base_query.filter(Conversation.user_id == user_id)
            
            # Total conversations
            total_conversations = base_query.count()
            
            # Active conversations (updated in last 7 days)
            week_ago = datetime.now() - timedelta(days=7)
            active_conversations = base_query.filter(
                Conversation.updated_at >= week_ago
            ).count()
            
            # Average conversation length
            avg_length_result = db.query(
                func.avg(func.count(Message.id))
            ).join(
                Conversation, Message.conversation_id == Conversation.id
            ).group_by(Conversation.id).scalar()
            
            avg_length = float(avg_length_result) if avg_length_result else 0.0
            
            # Stage distribution
            stage_distribution = {}
            stages = db.query(
                Conversation.stage,
                func.count(Conversation.id)
            ).group_by(Conversation.stage).all()
            
            for stage, count in stages:
                stage_distribution[stage or "initial"] = count
            
            # Completion rate (conversations with more than 5 messages)
            completed_conversations = db.query(Conversation).join(Message).group_by(
                Conversation.id
            ).having(func.count(Message.id) > 5).count()
            
            completion_rate = (completed_conversations / total_conversations * 100) if total_conversations > 0 else 0
            
            # User engagement metrics
            user_engagement = {
                "average_messages_per_conversation": avg_length,
                "return_user_rate": 85.0,  # Mock data
                "session_duration_minutes": 15.3  # Mock data
            }
            
            return ConversationAnalytics(
                total_conversations=total_conversations,
                active_conversations=active_conversations,
                average_length=avg_length,
                completion_rate=completion_rate,
                stage_distribution=stage_distribution,
                user_engagement=user_engagement
            )
            
        except Exception as e:
            print(f"Error analyzing conversations: {e}")
            return ConversationAnalytics(
                total_conversations=0,
                active_conversations=0,
                average_length=0.0,
                completion_rate=0.0,
                stage_distribution={},
                user_engagement={}
            )
    
    def _analyze_users(self, db: Session) -> UserAnalytics:
        try:
            # Total users
            total_users = db.query(User).count()
            
            # Active users (users with activity in last 30 days)
            month_ago = datetime.now() - timedelta(days=30)
            active_users = db.query(User).join(Conversation).filter(
                Conversation.updated_at >= month_ago
            ).distinct().count()
            
            # Retention rate calculation (simplified)
            retention_rate = (active_users / total_users * 100) if total_users > 0 else 0
            
            # Feature usage (mock data)
            feature_usage = {
                "multi_ai_personas": 67,
                "market_research": 43,
                "idea_mapping": 28,
                "conversation_export": 15
            }
            
            # User journey analysis (mock data)
            user_journey = [
                {"step": "signup", "users": total_users, "conversion_rate": 100.0},
                {"step": "first_chat", "users": int(total_users * 0.85), "conversion_rate": 85.0},
                {"step": "return_visit", "users": int(total_users * 0.60), "conversion_rate": 60.0},
                {"step": "power_user", "users": int(total_users * 0.25), "conversion_rate": 25.0}
            ]
            
            return UserAnalytics(
                total_users=total_users,
                active_users=active_users,
                retention_rate=retention_rate,
                average_session_length=18.5,  # Mock data
                feature_usage=feature_usage,
                user_journey=user_journey
            )
            
        except Exception as e:
            print(f"Error analyzing users: {e}")
            return UserAnalytics(
                total_users=0,
                active_users=0,
                retention_rate=0.0,
                average_session_length=0.0,
                feature_usage={},
                user_journey=[]
            )
    
    def _analyze_ideas(self, db: Session, user_id: Optional[int] = None) -> IdeaAnalytics:
        try:
            # Count conversations as proxy for ideas
            base_query = db.query(Conversation)
            if user_id:
                base_query = base_query.filter(Conversation.user_id == user_id)
            
            total_ideas = base_query.count()
            
            # Category distribution (based on conversation titles - simplified)
            category_distribution = {
                "Technology": int(total_ideas * 0.35),
                "Business": int(total_ideas * 0.25),
                "Healthcare": int(total_ideas * 0.15),
                "Education": int(total_ideas * 0.12),
                "Finance": int(total_ideas * 0.08),
                "Other": int(total_ideas * 0.05)
            }
            
            # Success metrics (mock data)
            success_metrics = {
                "completion_rate": 78.5,
                "user_satisfaction": 4.2,
                "idea_viability_score": 3.8,
                "market_potential_score": 3.6
            }
            
            # Trending concepts (mock data)
            trending_concepts = [
                "AI automation",
                "Sustainability solutions",
                "Remote work tools",
                "Health tech",
                "Fintech innovations"
            ]
            
            # AI persona effectiveness (mock data)
            ai_persona_effectiveness = {
                "socratic_mentor": 4.3,
                "business_analyst": 4.1,
                "technical_architect": 3.9,
                "creative_strategist": 4.0,
                "market_researcher": 3.8
            }
            
            return IdeaAnalytics(
                total_ideas=total_ideas,
                category_distribution=category_distribution,
                success_metrics=success_metrics,
                trending_concepts=trending_concepts,
                ai_persona_effectiveness=ai_persona_effectiveness
            )
            
        except Exception as e:
            print(f"Error analyzing ideas: {e}")
            return IdeaAnalytics(
                total_ideas=0,
                category_distribution={},
                success_metrics={},
                trending_concepts=[],
                ai_persona_effectiveness={}
            )
    
    def _analyze_system_performance(self, db: Session) -> SystemAnalytics:
        try:
            # API usage (mock data based on endpoint popularity)
            api_usage = {
                "chat": 1250,
                "conversations": 890,
                "market_research": 150,
                "idea_mapping": 85,
                "multi_perspective": 120,
                "auth": 450
            }
            
            # Response times (mock data)
            response_times = {
                "chat_endpoint": 1.2,
                "market_research": 3.8,
                "idea_mapping": 2.1,
                "auth": 0.8,
                "conversations": 0.5
            }
            
            # Error rates (mock data)
            error_rates = {
                "total": 2.3,
                "auth_errors": 1.1,
                "ai_timeout": 0.8,
                "database_errors": 0.4
            }
            
            # Popular features
            popular_features = [
                "Basic Chat",
                "Conversation History",
                "Market Research",
                "Multi-AI Personas",
                "Idea Mapping"
            ]
            
            # Growth metrics (mock data)
            growth_metrics = {
                "user_growth_rate": 15.2,
                "conversation_growth_rate": 23.7,
                "feature_adoption_rate": 8.9,
                "api_usage_growth": 12.1
            }
            
            return SystemAnalytics(
                api_usage=api_usage,
                response_times=response_times,
                error_rates=error_rates,
                popular_features=popular_features,
                growth_metrics=growth_metrics
            )
            
        except Exception as e:
            print(f"Error analyzing system performance: {e}")
            return SystemAnalytics(
                api_usage={},
                response_times={},
                error_rates={},
                popular_features=[],
                growth_metrics={}
            )
    
    def get_conversation_insights(self, db: Session, conversation_id: str) -> Dict[str, Any]:
        try:
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()
            
            if not conversation:
                return {"error": "Conversation not found"}
            
            messages = conversation.messages
            
            insights = {
                "conversation_id": conversation_id,
                "title": conversation.title,
                "stage": conversation.stage,
                "message_count": len(messages),
                "duration_days": (conversation.updated_at - conversation.created_at).days,
                "user_message_count": len([m for m in messages if m.role == "user"]),
                "ai_message_count": len([m for m in messages if m.role == "assistant"]),
                "average_message_length": sum(len(m.content) for m in messages) / len(messages) if messages else 0,
                "idea_evolution_score": 7.5,  # Mock score
                "engagement_score": 8.2,  # Mock score
                "key_topics": ["innovation", "technology", "market opportunity"],  # Mock data
                "sentiment_progression": [0.6, 0.7, 0.8, 0.75, 0.85],  # Mock data
            }
            
            return insights
            
        except Exception as e:
            print(f"Error getting conversation insights: {e}")
            return {"error": str(e)}
    
    def _get_mock_analytics(self) -> AnalyticsDashboard:
        return AnalyticsDashboard(
            conversation_analytics=ConversationAnalytics(
                total_conversations=0,
                active_conversations=0,
                average_length=0.0,
                completion_rate=0.0,
                stage_distribution={},
                user_engagement={}
            ),
            user_analytics=UserAnalytics(
                total_users=0,
                active_users=0,
                retention_rate=0.0,
                average_session_length=0.0,
                feature_usage={},
                user_journey=[]
            ),
            idea_analytics=IdeaAnalytics(
                total_ideas=0,
                category_distribution={},
                success_metrics={},
                trending_concepts=[],
                ai_persona_effectiveness={}
            ),
            system_analytics=SystemAnalytics(
                api_usage={},
                response_times={},
                error_rates={},
                popular_features=[],
                growth_metrics={}
            ),
            generated_at=datetime.now().isoformat()
        )