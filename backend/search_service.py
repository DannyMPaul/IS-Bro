from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from database import Conversation, Message
import re
from datetime import datetime, timedelta

class SearchService:
    def __init__(self):
        pass
    
    def search_conversations(self, 
                           db: Session, 
                           query: str, 
                           user_id: Optional[int] = None,
                           filters: Dict[str, Any] = {},
                           limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search through conversations and messages
        """
        try:
            # Start with base conversation query
            conversations_query = db.query(Conversation)
            
            # Filter by user if specified
            if user_id:
                conversations_query = conversations_query.filter(Conversation.user_id == user_id)
            
            # Apply filters
            if filters.get('stage'):
                conversations_query = conversations_query.filter(Conversation.stage == filters['stage'])
            
            if filters.get('date_from'):
                date_from = datetime.fromisoformat(filters['date_from'])
                conversations_query = conversations_query.filter(Conversation.created_at >= date_from)
            
            if filters.get('date_to'):
                date_to = datetime.fromisoformat(filters['date_to'])
                conversations_query = conversations_query.filter(Conversation.created_at <= date_to)
            
            # Search in conversation titles and messages
            search_terms = self._extract_search_terms(query)
            results = []
            
            # Search in conversation titles
            for term in search_terms:
                title_matches = conversations_query.filter(
                    Conversation.title.ilike(f'%{term}%')
                ).all()
                
                for conv in title_matches:
                    results.append({
                        'conversation': conv,
                        'relevance_score': 0.9,  # High relevance for title matches
                        'matching_snippet': conv.title,
                        'match_type': 'title'
                    })
            
            # Search in message content
            messages_query = db.query(Message).join(Conversation)
            if user_id:
                messages_query = messages_query.filter(Conversation.user_id == user_id)
            
            for term in search_terms:
                message_matches = messages_query.filter(
                    Message.content.ilike(f'%{term}%')
                ).all()
                
                for msg in message_matches:
                    snippet = self._extract_snippet(msg.content, term)
                    results.append({
                        'conversation': msg.conversation,
                        'relevance_score': 0.7,  # Medium relevance for content matches
                        'matching_snippet': snippet,
                        'match_type': 'content'
                    })
            
            # Remove duplicates and sort by relevance
            unique_results = self._deduplicate_results(results)
            unique_results.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            # Convert to response format
            search_results = []
            for result in unique_results[:limit]:
                conv = result['conversation']
                search_results.append({
                    'id': conv.id,
                    'title': conv.title,
                    'stage': conv.stage,
                    'created_at': conv.created_at.isoformat() + 'Z',
                    'updated_at': conv.updated_at.isoformat() + 'Z',
                    'message_count': len(conv.messages),
                    'relevance_score': result['relevance_score'],
                    'matching_snippet': result['matching_snippet']
                })
            
            return {
                'results': search_results,
                'total_count': len(unique_results),
                'query': query,
                'filters_applied': filters
            }
            
        except Exception as e:
            print(f"Error searching conversations: {e}")
            return {
                'results': [],
                'total_count': 0,
                'query': query,
                'filters_applied': filters
            }
    
    def _extract_search_terms(self, query: str) -> List[str]:
        """Extract search terms from query"""
        # Remove special characters and split by whitespace
        cleaned_query = re.sub(r'[^\w\s]', ' ', query.lower())
        terms = [term.strip() for term in cleaned_query.split() if len(term.strip()) > 2]
        return terms
    
    def _extract_snippet(self, content: str, term: str, context_length: int = 100) -> str:
        """Extract a snippet around the matching term"""
        content_lower = content.lower()
        term_lower = term.lower()
        
        # Find the term in the content
        index = content_lower.find(term_lower)
        if index == -1:
            return content[:context_length] + "..." if len(content) > context_length else content
        
        # Extract context around the term
        start = max(0, index - context_length // 2)
        end = min(len(content), index + len(term) + context_length // 2)
        
        snippet = content[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."
        
        return snippet
    
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate conversations, keeping highest relevance score"""
        seen_conversations = {}
        
        for result in results:
            conv_id = result['conversation'].id
            if conv_id not in seen_conversations or result['relevance_score'] > seen_conversations[conv_id]['relevance_score']:
                seen_conversations[conv_id] = result
        
        return list(seen_conversations.values())
    
    def get_search_suggestions(self, db: Session, partial_query: str, user_id: Optional[int] = None) -> List[str]:
        """Get search suggestions based on partial query"""
        try:
            suggestions = []
            
            # Get common words from conversation titles
            title_words = db.query(Conversation.title).all()
            all_words = set()
            
            for title_tuple in title_words:
                title = title_tuple[0] if title_tuple[0] else ""
                words = re.findall(r'\b\w{3,}\b', title.lower())
                all_words.update(words)
            
            # Filter words that start with partial query
            matching_words = [word for word in all_words if word.startswith(partial_query.lower())]
            
            # Sort by length (shorter words first, likely more common)
            matching_words.sort(key=len)
            
            return matching_words[:10]  # Return top 10 suggestions
            
        except Exception as e:
            print(f"Error getting search suggestions: {e}")
            return []
    
    def get_filter_options(self, db: Session, user_id: Optional[int] = None) -> Dict[str, List[str]]:
        """Get available filter options"""
        try:
            base_query = db.query(Conversation)
            if user_id:
                base_query = base_query.filter(Conversation.user_id == user_id)
            
            # Get available stages
            stages = db.query(Conversation.stage).distinct().all()
            stage_options = [stage[0] for stage in stages if stage[0]]
            
            # Get date ranges (last week, month, 3 months, year)
            now = datetime.now()
            date_options = [
                {'label': 'Last 7 days', 'value': '7d'},
                {'label': 'Last 30 days', 'value': '30d'},
                {'label': 'Last 3 months', 'value': '90d'},
                {'label': 'Last year', 'value': '1y'},
                {'label': 'All time', 'value': 'all'}
            ]
            
            return {
                'stages': stage_options,
                'date_ranges': date_options
            }
            
        except Exception as e:
            print(f"Error getting filter options: {e}")
            return {'stages': [], 'date_ranges': []}