"""
Database models for PostgreSQL persistence.
Uses SQLAlchemy ORM for database operations.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class QueryHistory(Base):
    """Query history for Q&A feature."""
    __tablename__ = 'query_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    query_id = Column(String(255), unique=True, nullable=False, index=True)
    
    # Query details
    user_query = Column(Text, nullable=False)
    sql_query = Column(Text)
    query_type = Column(String(50))  # 'sql', 'rag', 'hybrid'
    
    # Results
    result_data = Column(JSON)
    result_summary = Column(Text)
    
    # Performance
    execution_time = Column(Float)
    tokens_used = Column(Integer)
    
    # Metadata
    status = Column(String(50), default='success')  # success, failed, timeout
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_query_created', 'created_at'),
        Index('idx_query_status', 'status'),
    )
    
    def __repr__(self):
        return f"<QueryHistory(id={self.id}, query_id='{self.query_id}')>"


class LLMUsage(Base):
    """Track LLM API usage and costs."""
    __tablename__ = 'llm_usage'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # LLM details
    provider = Column(String(50), nullable=False)  # 'openai', 'anthropic', 'gemini'
    model = Column(String(100), nullable=False)
    
    # Usage metrics
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    
    # Cost tracking
    cost = Column(Float, default=0.0)
    
    # Context
    operation = Column(String(100))  # 'auto_analysis', 'rag_summary', 'query', etc.
    request_id = Column(String(255), index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_llm_provider_created', 'provider', 'created_at'),
        Index('idx_llm_operation_created', 'operation', 'created_at'),
    )
    
    def __repr__(self):
        return f"<LLMUsage(id={self.id}, provider='{self.provider}', model='{self.model}', tokens={self.total_tokens})>"



