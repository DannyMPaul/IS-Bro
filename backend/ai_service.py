from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from typing import List, Optional
import torch
import re
from datetime import datetime

from models import ConversationState, AIResponse, IdeaProposal, ConversationStage

class AIService:
    def __init__(self):
        self.model_name = "meta-llama/Llama-3.1-8B-Instruct"
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self._initialize_model()
    
    def _initialize_model(self):
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16,
                device_map="auto",
                load_in_8bit=True
            )
            
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_new_tokens=512,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
        except Exception as e:
            print(f"Model initialization failed: {e}")
            self.pipeline = None
    
    async def process_message(self, user_message: str, conversation: ConversationState) -> AIResponse:
        conversation.add_message("user", user_message)
        
        system_prompt = self._get_system_prompt(conversation.stage)
        context = self._build_context(conversation)
        
        full_prompt = f"{system_prompt}\n\n{context}\n\nUser: {user_message}\n\nBig Brother:"
        
        if self.pipeline:
            try:
                response = self.pipeline(full_prompt, max_new_tokens=300, temperature=0.7)[0]['generated_text']
                ai_response = self._extract_response(response, full_prompt)
            except Exception as e:
                ai_response = self._fallback_response(user_message, conversation.stage)
        else:
            ai_response = self._fallback_response(user_message, conversation.stage)
        
        suggestions = self._generate_suggestions(conversation.stage)
        should_advance = self._should_advance_stage(conversation)
        
        if should_advance:
            conversation.advance_stage()
        
        ai_response_obj = AIResponse(
            content=ai_response,
            suggestions=suggestions,
            should_advance_stage=should_advance
        )
        
        conversation.add_message("assistant", ai_response, suggestions)
        
        return ai_response_obj
    
    def _get_system_prompt(self, stage: ConversationStage) -> str:
        prompts = {
            ConversationStage.INITIAL: """You are Big Brother, a wise and slightly direct mentor who helps people refine vague ideas into concrete projects. You're like an experienced older sibling - supportive but challenging. 

Your goal is to understand their initial idea and start asking probing questions. Don't be overly formal. Be conversational but insightful.""",

            ConversationStage.EXPLORING: """Continue as Big Brother. Now dig deeper into their idea. Ask challenging questions about the problem they're solving, who would actually use this, and why it matters. Challenge weak assumptions but remain supportive.""",

            ConversationStage.STRUCTURING: """As Big Brother, help organize their thoughts into a clear structure. Start identifying: the core problem, target audience, proposed solution, potential impact, and constraints. Summarize what you've learned so far.""",

            ConversationStage.ALTERNATIVES: """Now suggest 2-3 alternative approaches or pivots to their idea. Present pros and cons for each. Help them see different angles they might not have considered.""",

            ConversationStage.REFINEMENT: """Focus on refining their chosen direction. Help them think through implementation details, potential challenges, and next steps.""",

            ConversationStage.PROPOSAL: """Prepare to create a structured project proposal based on everything discussed."""
        }
        return prompts.get(stage, prompts[ConversationStage.INITIAL])
    
    def _build_context(self, conversation: ConversationState) -> str:
        recent_messages = conversation.messages[-6:] if len(conversation.messages) > 6 else conversation.messages
        context = "\n".join([f"{msg.role.title()}: {msg.content}" for msg in recent_messages[:-1]])
        return context
    
    def _extract_response(self, full_response: str, prompt: str) -> str:
        try:
            response_start = full_response.find("Big Brother:") + len("Big Brother:")
            response = full_response[response_start:].strip()
            
            next_user_idx = response.find("User:")
            if next_user_idx != -1:
                response = response[:next_user_idx].strip()
            
            return response if response else "I need a moment to think about that. Can you tell me more?"
        except:
            return "I need a moment to think about that. Can you tell me more?"
    
    def _fallback_response(self, user_message: str, stage: ConversationStage) -> str:
        fallbacks = {
            ConversationStage.INITIAL: f"Interesting idea! Let me understand this better - what specific problem are you trying to solve with this concept?",
            ConversationStage.EXPLORING: f"That's helpful context. Now, who exactly would benefit from this solution? Can you paint me a picture of your ideal user?",
            ConversationStage.STRUCTURING: f"Good insights so far. Let me organize what I'm hearing - you're addressing [problem] for [audience] with [solution]. Is that accurate?",
            ConversationStage.ALTERNATIVES: f"Here are a few different angles to consider: 1) A simpler MVP approach, 2) Targeting a different user segment, 3) Focusing on one core feature first. Which resonates with you?",
            ConversationStage.REFINEMENT: f"Let's get practical. What would be the very first step you'd take to start building this? What's the minimum viable version?"
        }
        return fallbacks.get(stage, "Tell me more about your idea. What's the core problem you want to solve?")
    
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
        return conversation.interaction_count % 4 == 0 and conversation.interaction_count > 0
    
    async def generate_proposal(self, conversation: ConversationState) -> IdeaProposal:
        messages_text = "\n".join([f"{msg.role}: {msg.content}" for msg in conversation.messages])
        
        proposal_prompt = f"""Based on this conversation, create a structured project proposal:

{messages_text}

Generate a proposal with:
- Title (concise, descriptive)
- Summary (2-3 sentences)
- Problem (what it solves)
- Solution (how it works)
- Key Features (3-5 bullet points)
- Tech Stack (appropriate technologies)
- Next Steps (3-4 actionable items)

Format as JSON structure."""

        if self.pipeline:
            try:
                response = self.pipeline(proposal_prompt, max_new_tokens=400)[0]['generated_text']
                return self._parse_proposal(response, conversation)
            except:
                return self._create_fallback_proposal(conversation)
        else:
            return self._create_fallback_proposal(conversation)
    
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
    
    def _parse_proposal(self, response: str, conversation: ConversationState) -> IdeaProposal:
        try:
            return self._create_fallback_proposal(conversation)
        except:
            return self._create_fallback_proposal(conversation)
