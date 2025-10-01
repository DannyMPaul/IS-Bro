import google.generativeai as genai
from typing import Dict, List, Optional, Any
from enum import Enum
from dotenv import load_dotenv
import os

load_dotenv()

class AIProvider(str, Enum):
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"

class AIPersona(str, Enum):
    SOCRATIC_MENTOR = "socratic_mentor"
    BUSINESS_ANALYST = "business_analyst"
    TECHNICAL_ARCHITECT = "technical_architect"
    CREATIVE_STRATEGIST = "creative_strategist"
    MARKET_RESEARCHER = "market_researcher"

class MultiAIService:
    def __init__(self):
        # Initialize AI clients
        self.gemini_client = None
        self.openai_client = None
        self.anthropic_client = None
        
        # Initialize Gemini
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            try:
                genai.configure(api_key=gemini_key)
                self.gemini_client = genai.GenerativeModel('gemini-2.0-flash')
                print("Gemini client initialized successfully")
            except Exception as e:
                print(f"Failed to initialize Gemini: {e}")
        
        # Initialize OpenAI (only if available)
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                import openai
                self.openai_client = openai.OpenAI(api_key=openai_key)
                print("OpenAI client initialized successfully")
            except Exception as e:
                print(f"Failed to initialize OpenAI: {e}")
        
        # Initialize Anthropic (only if available)
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            try:
                import anthropic
                self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
                print("Anthropic client initialized successfully")
            except Exception as e:
                print(f"Failed to initialize Anthropic: {e}")
        
        self.persona_prompts = self._get_persona_prompts()
    
    def _get_persona_prompts(self) -> Dict[AIPersona, str]:
        return {
            AIPersona.SOCRATIC_MENTOR: """
            You are Big Brother, a Socratic mentor who helps refine ideas through thoughtful questioning.
            Your approach is gentle but probing, helping users think deeper about their concepts.
            Ask clarifying questions, challenge assumptions, and guide discovery rather than providing direct answers.
            """,
            
            AIPersona.BUSINESS_ANALYST: """
            You are a sharp business analyst focused on market viability, business models, and strategic planning.
            Analyze ideas from a commercial perspective: target market, revenue streams, competitive landscape, and scalability.
            Ask tough business questions and provide data-driven insights.
            """,
            
            AIPersona.TECHNICAL_ARCHITECT: """
            You are a senior technical architect who evaluates ideas from an implementation perspective.
            Focus on technical feasibility, architecture decisions, technology stack recommendations, and scalability concerns.
            Consider security, performance, and maintainability in your analysis.
            """,
            
            AIPersona.CREATIVE_STRATEGIST: """
            You are a creative strategist who thinks outside the box and explores innovative approaches.
            Push for creative solutions, alternative perspectives, and breakthrough thinking.
            Challenge conventional wisdom and encourage bold, innovative directions.
            """,
            
            AIPersona.MARKET_RESEARCHER: """
            You are a market research specialist who provides insights about industry trends, user needs, and market opportunities.
            Focus on market size, customer segments, competitive analysis, and emerging trends.
            Ground ideas in real market data and user research principles.
            """
        }
    
    def get_available_providers(self) -> List[AIProvider]:
        """Return list of available AI providers based on configured API keys"""
        available = []
        if self.gemini_client:
            available.append(AIProvider.GEMINI)
        if self.openai_client:
            available.append(AIProvider.OPENAI)
        if self.anthropic_client:
            available.append(AIProvider.ANTHROPIC)
        return available
    
    def get_response(self, 
                    message: str, 
                    persona: AIPersona = AIPersona.SOCRATIC_MENTOR,
                    provider: AIProvider = AIProvider.GEMINI,
                    conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Get AI response with specified persona and provider
        """
        try:
            # Build the prompt with persona context
            system_prompt = self.persona_prompts[persona]
            
            # Format conversation history
            context = ""
            if conversation_history:
                for msg in conversation_history[-5:]:  # Last 5 messages for context
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                    context += f"{role}: {content}\n"
            
            full_prompt = f"{system_prompt}\n\nConversation Context:\n{context}\n\nUser: {message}\n\nResponse:"
            
            # Route to appropriate AI provider
            if provider == AIProvider.GEMINI and self.gemini_client:
                return self._get_gemini_response(full_prompt, persona)
            elif provider == AIProvider.OPENAI and self.openai_client:
                return self._get_openai_response(full_prompt, persona, conversation_history)
            elif provider == AIProvider.ANTHROPIC and self.anthropic_client:
                return self._get_anthropic_response(full_prompt, persona)
            else:
                # Fallback to available provider
                available = self.get_available_providers()
                if available:
                    return self.get_response(message, persona, available[0], conversation_history)
                else:
                    raise Exception("No AI providers available")
                    
        except Exception as e:
            print(f"Error getting AI response: {e}")
            return {
                "response": "I apologize, but I'm having trouble processing your request right now. Please try again.",
                "provider": provider.value,
                "persona": persona.value,
                "error": str(e)
            }
    
    def _get_gemini_response(self, prompt: str, persona: AIPersona) -> Dict[str, Any]:
        try:
            response = self.gemini_client.generate_content(prompt)
            return {
                "response": response.text,
                "provider": AIProvider.GEMINI.value,
                "persona": persona.value,
                "model": "gemini-2.0-flash"
            }
        except Exception as e:
            raise Exception(f"Gemini API error: {e}")
    
    def _get_openai_response(self, prompt: str, persona: AIPersona, history: List[Dict] = None) -> Dict[str, Any]:
        try:
            messages = [{"role": "system", "content": prompt}]
            
            # Add conversation history
            if history:
                for msg in history[-5:]:
                    messages.append({
                        "role": msg.get('role', 'user'),
                        "content": msg.get('content', '')
                    })
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Use mini for cost efficiency
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            return {
                "response": response.choices[0].message.content,
                "provider": AIProvider.OPENAI.value,
                "persona": persona.value,
                "model": "gpt-4o-mini"
            }
        except Exception as e:
            raise Exception(f"OpenAI API error: {e}")
    
    def _get_anthropic_response(self, prompt: str, persona: AIPersona) -> Dict[str, Any]:
        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",  # Use Haiku for cost efficiency
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return {
                "response": response.content[0].text,
                "provider": AIProvider.ANTHROPIC.value,
                "persona": persona.value,
                "model": "claude-3-haiku"
            }
        except Exception as e:
            raise Exception(f"Anthropic API error: {e}")
    
    def get_multi_perspective_analysis(self, message: str, conversation_history: List[Dict] = None) -> List[Dict[str, Any]]:
        """
        Get responses from multiple personas for comprehensive analysis
        """
        perspectives = []
        available_providers = self.get_available_providers()
        
        # Define which personas to use for multi-perspective analysis
        key_personas = [
            AIPersona.SOCRATIC_MENTOR,
            AIPersona.BUSINESS_ANALYST,
            AIPersona.TECHNICAL_ARCHITECT
        ]
        
        # If no providers available, return empty list
        if not available_providers:
            return perspectives
        
        for i, persona in enumerate(key_personas):
            # Cycle through available providers (use modulo to wrap around)
            provider = available_providers[i % len(available_providers)]
            try:
                response = self.get_response(message, persona, provider, conversation_history)
                perspectives.append(response)
            except Exception as e:
                print(f"Failed to get {persona} perspective: {e}")
                continue
        
        return perspectives