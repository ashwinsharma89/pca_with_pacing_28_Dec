"""
Repository pattern for data access.
Provides clean abstraction over database operations.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from src.database.models import QueryHistory, LLMUsage

logger = logging.getLogger(__name__)


class BaseRepository:
    """Base repository with common operations."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def commit(self):
        """Commit transaction."""
        self.session.commit()
    
    def rollback(self):
        """Rollback transaction."""
        self.session.rollback()
    
    def flush(self):
        """Flush changes to database."""
        self.session.flush()





class QueryHistoryRepository(BaseRepository):
    """Repository for QueryHistory operations."""
    
    def create(self, query_data: Dict[str, Any]) -> QueryHistory:
        """Create a new query history entry."""
        query = QueryHistory(**query_data)
        self.session.add(query)
        self.session.flush()
        return query
    
    def get_by_id(self, query_id: int) -> Optional[QueryHistory]:
        """Get query by ID."""
        return self.session.query(QueryHistory).filter(QueryHistory.id == query_id).first()
    
    def get_recent(self, limit: int = 50) -> List[QueryHistory]:
        """Get recent queries."""
        return self.session.query(QueryHistory).order_by(
            desc(QueryHistory.created_at)
        ).limit(limit).all()
    
    def search_by_text(self, search_text: str, limit: int = 20) -> List[QueryHistory]:
        """Search queries by text."""
        return self.session.query(QueryHistory).filter(
            QueryHistory.user_query.ilike(f'%{search_text}%')
        ).order_by(desc(QueryHistory.created_at)).limit(limit).all()
    
    def get_by_status(self, status: str, limit: int = 100) -> List[QueryHistory]:
        """Get queries by status."""
        return self.session.query(QueryHistory).filter(
            QueryHistory.status == status
        ).order_by(desc(QueryHistory.created_at)).limit(limit).all()


class LLMUsageRepository(BaseRepository):
    """Repository for LLM usage tracking."""
    
    def create(self, usage_data: Dict[str, Any]) -> LLMUsage:
        """Create a new LLM usage entry."""
        usage = LLMUsage(**usage_data)
        self.session.add(usage)
        self.session.flush()
        return usage
    
    def get_usage_by_provider(self, provider: str, start_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get aggregated usage by provider."""
        from sqlalchemy import func
        
        query = self.session.query(
            func.sum(LLMUsage.total_tokens).label('total_tokens'),
            func.sum(LLMUsage.cost).label('total_cost'),
            func.count(LLMUsage.id).label('request_count')
        ).filter(LLMUsage.provider == provider)
        
        if start_date:
            query = query.filter(LLMUsage.created_at >= start_date)
        
        result = query.first()
        
        return {
            'provider': provider,
            'total_tokens': int(result.total_tokens or 0),
            'total_cost': float(result.total_cost or 0),
            'request_count': int(result.request_count or 0)
        }
    
    def get_usage_by_operation(self, operation: str, start_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get aggregated usage by operation."""
        from sqlalchemy import func
        
        query = self.session.query(
            func.sum(LLMUsage.total_tokens).label('total_tokens'),
            func.sum(LLMUsage.cost).label('total_cost'),
            func.count(LLMUsage.id).label('request_count')
        ).filter(LLMUsage.operation == operation)
        
        if start_date:
            query = query.filter(LLMUsage.created_at >= start_date)
        
        result = query.first()
        
        return {
            'operation': operation,
            'total_tokens': int(result.total_tokens or 0),
            'total_cost': float(result.total_cost or 0),
            'request_count': int(result.request_count or 0)
        }
    
    def get_total_usage(self, start_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get total usage across all providers."""
        from sqlalchemy import func
        
        query = self.session.query(
            func.sum(LLMUsage.total_tokens).label('total_tokens'),
            func.sum(LLMUsage.cost).label('total_cost'),
            func.count(LLMUsage.id).label('request_count')
        )
        
        if start_date:
            query = query.filter(LLMUsage.created_at >= start_date)
        
        result = query.first()
        
        return {
            'total_tokens': int(result.total_tokens or 0),
            'total_cost': float(result.total_cost or 0),
            'request_count': int(result.request_count or 0)
        }



