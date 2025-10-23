from typing import List, Dict, Optional, Any, Tuple
import json
from datetime import datetime
import google.generativeai as genai
from sqlalchemy.orm import Session
from sqlalchemy import desc
from dotenv import load_dotenv
import os

from models import (
    SummaryType, SummaryRequest, ConversationSummaryResponse,
    KeyPoint, IdeaTagCreate, IdeaCategoryCreate
)
from database import (
    ConversationSummary, IdeaTag, IdeaCategory,
    Message, Conversation, SessionLocal
)

# Load environment variables
load_dotenv()

# Configure Gemini AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class SummaryService:
    def __init__(self, db: Session):
        self.db = db
        self.model = genai.GenerativeModel('gemini-pro')

    async def generate_summary(self, request: SummaryRequest) -> ConversationSummaryResponse:
        """Generate a new summary for a conversation"""
        try:
            # Fetch conversation messages
            messages = (
                self.db.query(Message)
                .filter(Message.conversation_id == request.conversation_id)
                .order_by(Message.timestamp)
                .all()
            )

            if not messages:
                raise ValueError("No messages found for this conversation")

            # Convert messages to a format suitable for summarization
            conversation_text = self._format_conversation(messages)

            # Generate the appropriate summary based on type
            summary_content, key_points = await self._generate_summary_with_gemini(
                conversation_text,
                request.summary_type,
                include_key_points=request.include_key_points
            )

            # Calculate sentiment if requested
            sentiment_score = None
            if request.include_sentiment:
                sentiment_score = await self._analyze_sentiment(conversation_text)

            # Create new summary
            summary = ConversationSummary(
                conversation_id=request.conversation_id,
                summary_type=request.summary_type.value,
                content=summary_content,
                key_points=json.dumps(key_points) if key_points else None,
                sentiment_score=sentiment_score,
                completion_percentage=self._calculate_completion_percentage(messages)
            )

            # Extract and create tags and categories
            if key_points:
                await self._process_tags_and_categories(summary, key_points)

            self.db.add(summary)
            self.db.commit()
            self.db.refresh(summary)

            return self._convert_to_response(summary)

        except Exception as e:
            self.db.rollback()
            raise e

    async def get_summary(self, summary_id: int) -> ConversationSummaryResponse:
        """Retrieve an existing summary by ID"""
        summary = self.db.query(ConversationSummary).filter(ConversationSummary.id == summary_id).first()
        if not summary:
            raise ValueError("Summary not found")
        return self._convert_to_response(summary)

    async def get_conversation_summaries(self, conversation_id: str) -> List[ConversationSummaryResponse]:
        """Get all summaries for a conversation"""
        summaries = (
            self.db.query(ConversationSummary)
            .filter(ConversationSummary.conversation_id == conversation_id)
            .order_by(desc(ConversationSummary.created_at))
            .all()
        )
        return [self._convert_to_response(s) for s in summaries]

    def _format_conversation(self, messages: List[Message]) -> str:
        """Format conversation messages for AI processing"""
        formatted_messages = []
        for msg in messages:
            prefix = "User: " if msg.role == "user" else "Assistant: "
            formatted_messages.append(f"{prefix}{msg.content}")
        return "\n\n".join(formatted_messages)

    async def _generate_summary_with_gemini(
        self,
        conversation_text: str,
        summary_type: SummaryType,
        include_key_points: bool = True
    ) -> Tuple[str, Optional[List[Dict[str, Any]]]]:
        """Generate summary using Gemini AI"""
        # Create prompt based on summary type
        prompts = {
            SummaryType.BRIEF: "Provide a brief, concise summary of the main points discussed in this conversation:",
            SummaryType.DETAILED: "Create a detailed summary of the conversation, including all significant points and their context:",
            SummaryType.TECHNICAL: "Generate a technical summary focusing on specific technical details, requirements, and implementation points discussed:",
            SummaryType.ACTION_ITEMS: "Extract and list all action items, next steps, and decisions made in this conversation:"
        }

        base_prompt = prompts[summary_type]
        if include_key_points:
            base_prompt += "\n\nAlso identify key points in this format:\n{\"title\": \"point title\", \"description\": \"detailed explanation\", \"importance\": float 0-1, \"category\": \"relevant category\"}"

        # Generate response from Gemini
        response = await self.model.generate_content_async(
            f"{base_prompt}\n\nConversation:\n{conversation_text}"
        )

        # Parse response
        if include_key_points:
            # Split summary and key points
            parts = response.text.split("\nKey Points:", 1)
            summary_content = parts[0].strip()
            
            if len(parts) > 1:
                try:
                    # Extract and parse key points
                    key_points_text = parts[1].strip()
                    key_points = json.loads(f"[{key_points_text}]")
                except json.JSONDecodeError:
                    key_points = None
            else:
                key_points = None
        else:
            summary_content = response.text.strip()
            key_points = None

        return summary_content, key_points

    async def _analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment using Gemini AI"""
        prompt = "Analyze the sentiment of this conversation and return only a single float number between -1 (very negative) and 1 (very positive):\n\n"
        response = await self.model.generate_content_async(f"{prompt}{text}")
        try:
            return float(response.text.strip())
        except ValueError:
            return 0.0

    def _calculate_completion_percentage(self, messages: List[Message]) -> float:
        """Calculate conversation completion percentage based on stages and content"""
        if not messages:
            return 0.0
        
        # Count the number of user and assistant messages
        user_messages = sum(1 for m in messages if m.role == "user")
        assistant_messages = sum(1 for m in messages if m.role == "assistant")
        
        # More sophisticated completion calculation based on conversation flow
        completion_score = 0.0
        
        # Basic progress from message count
        if user_messages >= 1:
            completion_score += 0.2  # Started
        if assistant_messages >= 1:
            completion_score += 0.2  # Got initial response
        if user_messages >= 3:
            completion_score += 0.2  # Continued engagement
        if assistant_messages >= 3:
            completion_score += 0.2  # Developed discussion
            
        # Look for completion indicators in messages
        for msg in messages[-3:]:  # Check last 3 messages
            content = msg.content.lower()
            if any(word in content for word in ["conclude", "finalize", "complete", "finish"]):
                completion_score += 0.1
            if "next steps" in content or "action items" in content:
                completion_score += 0.1
                
        return min(completion_score, 1.0)

    async def _process_tags_and_categories(self, summary: ConversationSummary, key_points: List[Dict[str, Any]]):
        """Process and create tags and categories from key points"""
        for point in key_points:
            if "category" in point and point["category"]:
                # Create or get category
                category = (
                    self.db.query(IdeaCategory)
                    .filter(IdeaCategory.name == point["category"])
                    .first()
                )
                if not category:
                    category = IdeaCategory(
                        name=point["category"],
                        description=f"Auto-generated category from summary {summary.id}"
                    )
                    self.db.add(category)
                summary.categories.append(category)

            # Create tags from key point title
            tag_name = point["title"].lower().replace(" ", "_")
            tag = (
                self.db.query(IdeaTag)
                .filter(IdeaTag.name == tag_name)
                .first()
            )
            if not tag:
                tag = IdeaTag(
                    name=tag_name,
                    description=point["description"]
                )
                self.db.add(tag)
            summary.tags.append(tag)

    def _convert_to_response(self, summary: ConversationSummary) -> ConversationSummaryResponse:
        """Convert database model to response model"""
        key_points = (
            json.loads(summary.key_points)
            if summary.key_points
            else None
        )

        return ConversationSummaryResponse(
            summary_id=summary.id,
            conversation_id=summary.conversation_id,
            summary_type=SummaryType(summary.summary_type),
            content=summary.content,
            key_points=[KeyPoint(**kp) for kp in key_points] if key_points else None,
            sentiment_score=summary.sentiment_score,
            completion_percentage=summary.completion_percentage,
            categories=[c.name for c in summary.categories],
            tags=[t.name for t in summary.tags],
            created_at=summary.created_at,
            updated_at=summary.updated_at
        )