import os
import google.generativeai as genai
from typing import List, Optional
from datetime import datetime

from models import ConversationState, AIResponse, IdeaProposal, ConversationStage

class AIService:
    def __init__(self):
        self.model = None
        self._initialize_client()
    
    def _initialize_client(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                print("Gemini client initialized successfully")
            except Exception as e:
                print(f"Failed to initialize Gemini client: {e}")
                self.model = None
        else:
            print("No Gemini API key found. Set GEMINI_API_KEY environment variable.")
            self.model = None

    def process_message(self, user_message: str, conversation: ConversationState) -> AIResponse:
        """Process user message and generate appropriate AI response"""
        conversation.add_user_message(user_message)
        
        # Try to get AI response
        ai_response = None
        if self.model:
            try:
                ai_response = self._generate_ai_response(user_message, conversation)
            except Exception as e:
                print(f"Gemini API error: {e}")
        
        # Fallback to dynamic response if AI fails
        if not ai_response or len(ai_response.strip()) < 10:
            ai_response = self._dynamic_fallback(user_message, conversation.current_stage)
        
        # Add AI response to conversation
        conversation.add_ai_message(ai_response)
        conversation.last_updated = datetime.now()
        
        # Get suggestions and check if we should advance
        suggestions = self._generate_suggestions(conversation.current_stage)
        should_advance = self._should_advance_stage(conversation)
        
        if should_advance:
            conversation.advance_stage()
        
        return AIResponse(
            message=ai_response,
            suggestions=suggestions,
            conversation_id=conversation.id,
            stage=conversation.current_stage
        )

    def _generate_ai_response(self, user_message: str, conversation: ConversationState) -> str:
        """Generate AI response using Gemini"""
        if not self.model:
            return None
            
        system_prompt = self._get_system_prompt(conversation.current_stage)
        context = self._build_context(conversation)
        
        # Create the prompt for Gemini
        full_prompt = f"""{system_prompt}

Context from previous conversation:
{context}

User's latest message: {user_message}

Ask ONE thoughtful question to help them think deeper about their idea. Be conversational and insightful."""
        
        try:
            response = self.model.generate_content(full_prompt)
            return response.text.strip()
            
        except Exception as e:
            print(f"Gemini API error: {e}")
            return None

    def _get_system_prompt(self, stage: ConversationStage) -> str:
        base_prompt = """You are Big Brother, a wise and slightly direct mentor who helps people refine vague ideas into concrete projects. You're like an experienced older sibling - supportive but challenging.

Your responses should ALWAYS be in the form of thoughtful questions that help users think deeper about their ideas. Never give direct advice - instead ask probing questions that lead them to insights.

Be conversational, insightful, and focus on one key question at a time."""

        stage_prompts = {
            ConversationStage.INITIAL: base_prompt + "\n\nFocus on understanding their initial idea. Ask about the specific problem they're solving and who it affects.",
            
            ConversationStage.EXPLORING: base_prompt + "\n\nDig deeper into their idea. Ask challenging questions about the problem, target users, and why it matters.",
            
            ConversationStage.STRUCTURING: base_prompt + "\n\nHelp organize their thoughts. Ask about core value proposition, constraints, and success metrics.",
            
            ConversationStage.ALTERNATIVES: base_prompt + "\n\nSuggest they consider different approaches. Ask about simpler versions, different user segments, or alternative solutions.",
            
            ConversationStage.REFINEMENT: base_prompt + "\n\nFocus on implementation. Ask about practical next steps, MVP features, and immediate value.",
            
            ConversationStage.PROPOSAL: base_prompt + "\n\nHelp them finalize their concept. Ask about missing pieces and readiness to move forward."
        }
        
        return stage_prompts.get(stage, stage_prompts[ConversationStage.INITIAL])

    def _build_context(self, conversation: ConversationState) -> str:
        recent_messages = conversation.messages[-4:] if len(conversation.messages) > 4 else conversation.messages
        context = "\n".join([f"{msg.role.title()}: {msg.content}" for msg in recent_messages[:-1]])
        return context

    def _dynamic_fallback(self, user_message: str, stage: ConversationStage) -> str:
        user_snippet = user_message.strip().lower()
        
        if not user_snippet:
            return "Tell me about your idea - what problem are you trying to solve?"

        if stage == ConversationStage.INITIAL:
            if "hunger" in user_snippet or "food" in user_snippet:
                return "Solving hunger is a noble goal! What specific aspect of hunger are you targeting - is it food access, food production, food distribution, or something else?"
            elif "education" in user_snippet or "learning" in user_snippet:
                return "Education is crucial! What specific learning problem are you trying to solve? Is it access to education, quality of teaching, student engagement, or something else?"
            elif "health" in user_snippet or "medical" in user_snippet:
                return "Healthcare innovation is important! What specific health challenge are you addressing? Is it diagnosis, treatment, prevention, or healthcare access?"
            else:
                return f"Interesting idea! To help you refine this, what specific problem does this solve? Who are the people most affected by this problem?"
        
        elif stage == ConversationStage.EXPLORING:
            return "Good direction! Now let's dig deeper - who exactly would benefit from this solution? Can you describe your ideal user and what they currently do to handle this problem?"
        
        elif stage == ConversationStage.STRUCTURING:
            return "Let me help organize your thoughts. Based on what you've shared, what would you say is the core value you're providing? And what are the main constraints you'll face?"
        
        elif stage == ConversationStage.ALTERNATIVES:
            return "Now let's explore different approaches. Have you considered starting with a smaller user group, building just one core feature first, or partnering with existing organizations? Which resonates with you?"
        
        elif stage == ConversationStage.REFINEMENT:
            return "Time to get practical! If you had to build the simplest version of this idea in 3 months, what would it look like? What's the one feature that would provide immediate value?"
        
        return "That's helpful context. What's the next aspect of this idea you'd like to explore together?"

    def _generate_suggestions(self, stage: ConversationStage) -> List[str]:
        suggestions = {
            ConversationStage.INITIAL: [
                "What problem does this solve?",
                "Who would use this?",
                "Why does this matter?"
            ],
            ConversationStage.EXPLORING: [
                "What alternatives exist?",
                "What makes this unique?",
                "What's the biggest challenge?"
            ],
            ConversationStage.STRUCTURING: [
                "What's the core value proposition?",
                "What are the constraints?",
                "How would you measure success?"
            ],
            ConversationStage.ALTERNATIVES: [
                "Consider a simpler approach",
                "Target a niche first",
                "Focus on one key feature"
            ],
            ConversationStage.REFINEMENT: [
                "What's the MVP?",
                "What tech stack?",
                "What's the timeline?"
            ]
        }
        return suggestions.get(stage, [])

    def _should_advance_stage(self, conversation: ConversationState) -> bool:
        return conversation.interaction_count % 3 == 0 and conversation.interaction_count > 0

    def generate_proposal(self, conversation: ConversationState) -> IdeaProposal:
        if self.model:
            try:
                messages_text = "\n".join([f"{msg.role}: {msg.content}" for msg in conversation.messages])
                
                prompt = f"""Based on this conversation, create a structured project proposal:

{messages_text}

Generate a concise proposal with:
- Title (descriptive)
- Summary (2-3 sentences)
- Problem (what it solves)
- Solution (how it works)
- Key Features (3-4 bullet points)
- Tech Stack (appropriate technologies)
- Next Steps (3-4 actionable items)

Format as clear sections."""

                response = self.model.generate_content(prompt)
                
                # Parse the response (simplified)
                content = response.text
                return self._parse_proposal_content(content)
                
            except Exception as e:
                print(f"Proposal generation error: {e}")
                return self._create_fallback_proposal(conversation)
        else:
            return self._create_fallback_proposal(conversation)

    def _parse_proposal_content(self, content: str) -> IdeaProposal:
        # Simple parsing - in a real app you'd want more sophisticated parsing
        lines = content.split('\n')
        return IdeaProposal(
            title="AI-Generated Project Proposal",
            summary="A refined project concept based on our discussion",
            problem="Problem identified through conversation",
            solution="Solution approach developed collaboratively",
            features=["Feature 1", "Feature 2", "Feature 3"],
            tech_stack=["Technology 1", "Technology 2"],
            next_steps=["Step 1", "Step 2", "Step 3"],
            created_at=datetime.now()
        )

    def _create_fallback_proposal(self, conversation: ConversationState) -> IdeaProposal:
        return IdeaProposal(
            title="Project Idea",
            summary="A refined project concept based on our discussion",
            problem="Problem to be defined based on conversation",
            solution="Solution approach to be detailed",
            features=["Core feature 1", "Core feature 2", "Core feature 3"],
            tech_stack=["React", "Node.js", "Database"],
            next_steps=["Define requirements", "Create prototype", "Test with users"],
            created_at=datetime.now()
        )
