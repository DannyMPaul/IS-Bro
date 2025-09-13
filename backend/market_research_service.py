import requests
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import os
from dotenv import load_dotenv

load_dotenv()

class MarketDataSource(str, Enum):
    ALPHA_VANTAGE = "alpha_vantage"
    NEWS_API = "news_api"
    SERP_API = "serp_api"
    CRUNCHBASE = "crunchbase"

@dataclass
class MarketTrend:
    keyword: str
    interest_score: float
    growth_rate: float
    related_topics: List[str]
    time_period: str

@dataclass
class CompetitorInfo:
    name: str
    description: str
    funding: Optional[str]
    market_share: Optional[float]
    key_features: List[str]
    url: Optional[str]

@dataclass
class IndustryInsight:
    industry: str
    market_size: Optional[str]
    growth_rate: Optional[float]
    key_trends: List[str]
    challenges: List[str]
    opportunities: List[str]

@dataclass
class MarketResearchReport:
    query: str
    industry_insights: IndustryInsight
    competitors: List[CompetitorInfo]
    market_trends: List[MarketTrend]
    news_headlines: List[str]
    recommendations: List[str]
    research_timestamp: str

class MarketResearchService:
    def __init__(self):
        # API keys
        self.news_api_key = os.getenv("NEWS_API_KEY")
        self.serp_api_key = os.getenv("SERP_API_KEY")
        self.crunchbase_key = os.getenv("CRUNCHBASE_API_KEY")
        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        
        # Base URLs
        self.news_api_url = "https://newsapi.org/v2"
        self.serp_api_url = "https://serpapi.com/search"
        
        print("Market Research Service initialized")
        self._log_available_sources()
    
    def _log_available_sources(self):
        """Log which market data sources are available"""
        available = []
        if self.news_api_key:
            available.append("News API")
        if self.serp_api_key:
            available.append("SERP API")
        if self.crunchbase_key:
            available.append("Crunchbase")
        if self.alpha_vantage_key:
            available.append("Alpha Vantage")
        
        if available:
            print(f"Available market data sources: {', '.join(available)}")
        else:
            print("No market research API keys configured - using mock data")
    
    async def conduct_market_research(self, idea: str, industry: str = None) -> MarketResearchReport:
        """
        Conduct comprehensive market research for an idea
        """
        try:
            # Extract key terms from the idea
            keywords = self._extract_keywords(idea)
            
            # Parallel research tasks
            industry_insights = await self._get_industry_insights(industry or keywords[0] if keywords else "technology")
            competitors = await self._find_competitors(keywords)
            market_trends = await self._analyze_market_trends(keywords)
            news = await self._get_relevant_news(keywords)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                idea, industry_insights, competitors, market_trends
            )
            
            return MarketResearchReport(
                query=idea,
                industry_insights=industry_insights,
                competitors=competitors,
                market_trends=market_trends,
                news_headlines=news,
                recommendations=recommendations,
                research_timestamp=str(datetime.now())
            )
            
        except Exception as e:
            print(f"Error conducting market research: {e}")
            # Return mock data if APIs fail
            return self._get_mock_research_data(idea)
    
    def _extract_keywords(self, idea: str) -> List[str]:
        """Extract key terms from idea description"""
        # Simple keyword extraction (in production, use NLP)
        import re
        # Remove common words and extract meaningful terms
        stop_words = {"a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should"}
        
        words = re.findall(r'\b\w+\b', idea.lower())
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        
        return keywords[:5]  # Return top 5 keywords
    
    async def _get_industry_insights(self, industry: str) -> IndustryInsight:
        """Get industry insights and market data"""
        try:
            # Mock industry data (in production, integrate with industry databases)
            industry_data = {
                "technology": {
                    "market_size": "$5.2 trillion",
                    "growth_rate": 8.2,
                    "trends": ["AI/ML adoption", "Cloud migration", "Cybersecurity focus", "Remote work tools"],
                    "challenges": ["Data privacy regulations", "Talent shortage", "Economic uncertainty"],
                    "opportunities": ["Emerging markets", "SMB digitization", "Sustainability tech"]
                },
                "healthcare": {
                    "market_size": "$4.5 trillion",
                    "growth_rate": 7.9,
                    "trends": ["Telemedicine", "AI diagnostics", "Personalized medicine", "Digital health"],
                    "challenges": ["Regulatory compliance", "Data security", "Cost pressures"],
                    "opportunities": ["Aging population", "Preventive care", "Digital therapeutics"]
                },
                "fintech": {
                    "market_size": "$310 billion",
                    "growth_rate": 13.7,
                    "trends": ["Digital payments", "DeFi", "RegTech", "Open banking"],
                    "challenges": ["Regulation", "Cybersecurity", "Market saturation"],
                    "opportunities": ["Emerging markets", "SMB lending", "Insurance tech"]
                }
            }
            
            data = industry_data.get(industry.lower(), industry_data["technology"])
            
            return IndustryInsight(
                industry=industry,
                market_size=data["market_size"],
                growth_rate=data["growth_rate"],
                key_trends=data["trends"],
                challenges=data["challenges"],
                opportunities=data["opportunities"]
            )
            
        except Exception as e:
            print(f"Error getting industry insights: {e}")
            return IndustryInsight(
                industry=industry,
                market_size="Data unavailable",
                growth_rate=None,
                key_trends=["Market research in progress"],
                challenges=["Data collection needed"],
                opportunities=["Analysis pending"]
            )
    
    async def _find_competitors(self, keywords: List[str]) -> List[CompetitorInfo]:
        """Find potential competitors using search APIs"""
        competitors = []
        
        try:
            if self.serp_api_key and keywords:
                # Search for competitors using SERP API
                query = f"{' '.join(keywords[:2])} startup company"
                params = {
                    "engine": "google",
                    "q": query,
                    "api_key": self.serp_api_key,
                    "num": 5
                }
                
                response = requests.get(self.serp_api_url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    organic_results = data.get("organic_results", [])
                    
                    for result in organic_results[:3]:
                        competitors.append(CompetitorInfo(
                            name=result.get("title", "Unknown"),
                            description=result.get("snippet", ""),
                            funding=None,
                            market_share=None,
                            key_features=[],
                            url=result.get("link")
                        ))
            
            # If no API or no results, add mock competitors
            if not competitors:
                mock_competitors = [
                    CompetitorInfo(
                        name="InnovateTech Solutions",
                        description="Leading provider in the space with proven track record",
                        funding="$15M Series A",
                        market_share=15.0,
                        key_features=["Enterprise focus", "AI-powered", "Scalable platform"],
                        url="https://example.com"
                    ),
                    CompetitorInfo(
                        name="NextGen Dynamics",
                        description="Emerging player with innovative approach",
                        funding="$5M Seed",
                        market_share=8.0,
                        key_features=["User-friendly", "Cost-effective", "Fast deployment"],
                        url="https://example.com"
                    )
                ]
                competitors.extend(mock_competitors)
                
        except Exception as e:
            print(f"Error finding competitors: {e}")
        
        return competitors
    
    async def _analyze_market_trends(self, keywords: List[str]) -> List[MarketTrend]:
        """Analyze market trends for the given keywords"""
        trends = []
        
        try:
            # Mock trend data (in production, integrate with Google Trends API or similar)
            for keyword in keywords[:3]:
                trends.append(MarketTrend(
                    keyword=keyword,
                    interest_score=85.0,  # Mock score
                    growth_rate=12.5,     # Mock growth
                    related_topics=[f"{keyword} automation", f"{keyword} AI", f"{keyword} cloud"],
                    time_period="Last 12 months"
                ))
                
        except Exception as e:
            print(f"Error analyzing market trends: {e}")
        
        return trends
    
    async def _get_relevant_news(self, keywords: List[str]) -> List[str]:
        """Get relevant news headlines"""
        headlines = []
        
        try:
            if self.news_api_key and keywords:
                query = " OR ".join(keywords[:2])
                params = {
                    "q": query,
                    "sortBy": "publishedAt",
                    "language": "en",
                    "pageSize": 5,
                    "apiKey": self.news_api_key
                }
                
                response = requests.get(f"{self.news_api_url}/everything", params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get("articles", [])
                    headlines = [article["title"] for article in articles[:5]]
            
            # Add mock headlines if no API results
            if not headlines:
                headlines = [
                    "Industry sees 25% growth in innovative solutions",
                    "New regulations impact market dynamics",
                    "Funding increases for emerging technologies",
                    "Consumer demand shifts toward digital alternatives",
                    "Market leaders announce strategic partnerships"
                ]
                
        except Exception as e:
            print(f"Error getting relevant news: {e}")
            headlines = ["Market research API temporarily unavailable"]
        
        return headlines
    
    def _generate_recommendations(self, 
                                idea: str, 
                                industry: IndustryInsight, 
                                competitors: List[CompetitorInfo],
                                trends: List[MarketTrend]) -> List[str]:
        """Generate strategic recommendations based on research"""
        recommendations = []
        
        # Market positioning
        if competitors:
            recommendations.append(f"Consider differentiation from {len(competitors)} identified competitors through unique value proposition")
        
        # Industry trends
        if industry.key_trends:
            recommendations.append(f"Align with key industry trends: {', '.join(industry.key_trends[:2])}")
        
        # Market opportunities
        if industry.opportunities:
            recommendations.append(f"Explore opportunities in: {', '.join(industry.opportunities[:2])}")
        
        # Growth potential
        if industry.growth_rate and industry.growth_rate > 5:
            recommendations.append(f"Industry shows strong growth potential at {industry.growth_rate}% annually")
        
        # Risk mitigation
        if industry.challenges:
            recommendations.append(f"Address key industry challenges: {industry.challenges[0]}")
        
        return recommendations
    
    def _get_mock_research_data(self, idea: str) -> MarketResearchReport:
        """Return mock data when APIs are unavailable"""
        return MarketResearchReport(
            query=idea,
            industry_insights=IndustryInsight(
                industry="Technology",
                market_size="$500B+",
                growth_rate=12.0,
                key_trends=["AI adoption", "Digital transformation", "Remote solutions"],
                challenges=["Competition", "Regulation", "Talent shortage"],
                opportunities=["Emerging markets", "SMB sector", "Automation"]
            ),
            competitors=[
                CompetitorInfo(
                    name="Market Leader Inc",
                    description="Established player with comprehensive solution",
                    funding="$50M+",
                    market_share=25.0,
                    key_features=["Enterprise grade", "Proven scale"],
                    url=None
                )
            ],
            market_trends=[
                MarketTrend(
                    keyword="innovation",
                    interest_score=90.0,
                    growth_rate=15.0,
                    related_topics=["automation", "AI", "efficiency"],
                    time_period="12 months"
                )
            ],
            news_headlines=["Market shows strong growth potential", "New innovations drive adoption"],
            recommendations=["Focus on unique differentiation", "Consider enterprise market", "Plan for scalability"],
            research_timestamp=str(datetime.now())
        )

from datetime import datetime