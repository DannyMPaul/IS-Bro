from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import json

class TemplateCategory(str, Enum):
    TECHNOLOGY = "technology"
    BUSINESS = "business"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    SUSTAINABILITY = "sustainability"
    ENTERTAINMENT = "entertainment"
    PRODUCTIVITY = "productivity"

@dataclass
class ConversationTemplate:
    id: str
    title: str
    category: TemplateCategory
    description: str
    initial_prompt: str
    suggested_questions: List[str]
    target_audience: str
    estimated_duration: str
    difficulty_level: str
    tags: List[str]

class TemplateService:
    def __init__(self):
        self.templates = self._load_default_templates()
    
    def _load_default_templates(self) -> List[ConversationTemplate]:
        """Load default conversation templates"""
        return [
            ConversationTemplate(
                id="tech_startup_idea",
                title="Tech Startup Idea",
                category=TemplateCategory.TECHNOLOGY,
                description="Explore and refine a technology-based startup concept",
                initial_prompt="I have an idea for a tech startup that could solve a problem I've been thinking about.",
                suggested_questions=[
                    "What specific problem does your tech solution address?",
                    "Who would be your target users?",
                    "What technology stack would you consider?",
                    "How would you monetize this solution?"
                ],
                target_audience="Entrepreneurs, Developers",
                estimated_duration="20-30 minutes",
                difficulty_level="Medium",
                tags=["startup", "technology", "business", "MVP"]
            ),
            ConversationTemplate(
                id="mobile_app_concept",
                title="Mobile App Development",
                category=TemplateCategory.TECHNOLOGY,
                description="Design and plan a mobile application from concept to launch",
                initial_prompt="I want to create a mobile app that would make people's daily lives easier.",
                suggested_questions=[
                    "What daily problem would your app solve?",
                    "Would this be iOS, Android, or cross-platform?",
                    "What would be the core features?",
                    "How would users discover and use your app?"
                ],
                target_audience="App Developers, Product Managers",
                estimated_duration="25-35 minutes",
                difficulty_level="Medium",
                tags=["mobile", "app", "UX", "development"]
            ),
            ConversationTemplate(
                id="social_impact_project",
                title="Social Impact Initiative",
                category=TemplateCategory.SUSTAINABILITY,
                description="Develop a project that creates positive social or environmental impact",
                initial_prompt="I want to start a project that makes a positive difference in my community or the world.",
                suggested_questions=[
                    "What social or environmental issue concerns you most?",
                    "What resources do you currently have available?",
                    "Who would you need to partner with?",
                    "How would you measure success?"
                ],
                target_audience="Social Entrepreneurs, Activists",
                estimated_duration="30-40 minutes",
                difficulty_level="High",
                tags=["social impact", "community", "sustainability", "non-profit"]
            ),
            ConversationTemplate(
                id="online_business",
                title="Online Business Venture",
                category=TemplateCategory.BUSINESS,
                description="Plan and structure an online business or e-commerce venture",
                initial_prompt="I want to start an online business but I'm not sure what direction to take.",
                suggested_questions=[
                    "What skills or interests could you monetize?",
                    "What's your target market?",
                    "How much initial investment can you make?",
                    "What would differentiate you from competitors?"
                ],
                target_audience="Entrepreneurs, Side Hustlers",
                estimated_duration="25-30 minutes",
                difficulty_level="Medium",
                tags=["e-commerce", "online business", "marketing", "revenue"]
            ),
            ConversationTemplate(
                id="creative_project",
                title="Creative Content Project",
                category=TemplateCategory.ENTERTAINMENT,
                description="Develop a creative project like a blog, YouTube channel, or artistic venture",
                initial_prompt="I have creative ideas that I want to turn into something people would enjoy and engage with.",
                suggested_questions=[
                    "What type of content excites you most?",
                    "Who would be your audience?",
                    "What platform would work best?",
                    "How often could you create content?"
                ],
                target_audience="Content Creators, Artists",
                estimated_duration="20-25 minutes",
                difficulty_level="Low",
                tags=["content", "creative", "audience", "platform"]
            ),
            ConversationTemplate(
                id="productivity_tool",
                title="Productivity Solution",
                category=TemplateCategory.PRODUCTIVITY,
                description="Create a tool or system to improve personal or team productivity",
                initial_prompt="I want to build something that helps people be more productive and organized.",
                suggested_questions=[
                    "What productivity challenges do you face personally?",
                    "Would this be a digital tool or physical system?",
                    "Who else struggles with similar issues?",
                    "What existing solutions fall short?"
                ],
                target_audience="Product Managers, Developers",
                estimated_duration="20-30 minutes",
                difficulty_level="Medium",
                tags=["productivity", "tools", "workflow", "efficiency"]
            ),
            ConversationTemplate(
                id="educational_platform",
                title="Educational Innovation",
                category=TemplateCategory.EDUCATION,
                description="Design an educational program, course, or learning platform",
                initial_prompt="I want to create something that helps people learn a skill or subject more effectively.",
                suggested_questions=[
                    "What subject or skill would you focus on?",
                    "What's wrong with current learning methods?",
                    "What age group or audience would you target?",
                    "How would you make learning engaging?"
                ],
                target_audience="Educators, Course Creators",
                estimated_duration="25-35 minutes",
                difficulty_level="Medium",
                tags=["education", "learning", "curriculum", "engagement"]
            ),
            ConversationTemplate(
                id="health_wellness",
                title="Health & Wellness Solution",
                category=TemplateCategory.HEALTHCARE,
                description="Develop a health, fitness, or wellness-focused solution",
                initial_prompt="I want to create something that helps people improve their health and well-being.",
                suggested_questions=[
                    "What specific health issue would you address?",
                    "Would this be preventive or treatment-focused?",
                    "What expertise do you have in health/wellness?",
                    "How would you ensure safety and efficacy?"
                ],
                target_audience="Health Professionals, Wellness Coaches",
                estimated_duration="30-35 minutes",
                difficulty_level="High",
                tags=["health", "wellness", "fitness", "prevention"]
            )
        ]
    
    def get_all_templates(self) -> List[ConversationTemplate]:
        """Get all available templates"""
        return self.templates
    
    def get_templates_by_category(self, category: TemplateCategory) -> List[ConversationTemplate]:
        """Get templates filtered by category"""
        return [t for t in self.templates if t.category == category]
    
    def get_template_by_id(self, template_id: str) -> ConversationTemplate:
        """Get a specific template by ID"""
        for template in self.templates:
            if template.id == template_id:
                return template
        return None
    
    def search_templates(self, query: str) -> List[ConversationTemplate]:
        """Search templates by title, description, or tags"""
        query = query.lower()
        results = []
        
        for template in self.templates:
            if (query in template.title.lower() or 
                query in template.description.lower() or
                any(query in tag.lower() for tag in template.tags)):
                results.append(template)
        
        return results
    
    def get_categories(self) -> List[str]:
        """Get all available categories"""
        return [category.value for category in TemplateCategory]

# Convert template to dictionary for JSON serialization
def template_to_dict(template: ConversationTemplate) -> Dict[str, Any]:
    return {
        "id": template.id,
        "title": template.title,
        "category": template.category.value,
        "description": template.description,
        "initial_prompt": template.initial_prompt,
        "suggested_questions": template.suggested_questions,
        "target_audience": template.target_audience,
        "estimated_duration": template.estimated_duration,
        "difficulty_level": template.difficulty_level,
        "tags": template.tags
    }