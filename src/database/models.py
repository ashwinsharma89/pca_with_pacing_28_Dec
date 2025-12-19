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


class Campaign(Base):
    """Campaign data model."""
    __tablename__ = 'campaigns'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(String(255), unique=True, nullable=False, index=True)
    campaign_name = Column(String(500), nullable=False)
    platform = Column(String(100), nullable=False, index=True)
    channel = Column(String(100), index=True)
    
    # Metrics
    spend = Column(Float, default=0.0)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    ctr = Column(Float, default=0.0)
    cpc = Column(Float, default=0.0)
    cpa = Column(Float, default=0.0)
    roas = Column(Float)
    
    # Metadata
    date = Column(DateTime, index=True)
    funnel_stage = Column(String(50), index=True)
    objective = Column(String(100), index=True)  # Campaign objective (Awareness, Traffic, Conversions)
    audience = Column(String(255))
    creative_type = Column(String(100))
    placement = Column(String(255))
    
    # Additional data stored as JSON
    additional_data = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    analyses = relationship("Analysis", back_populates="campaign", cascade="all, delete-orphan")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_campaign_platform_date', 'platform', 'date'),
        Index('idx_campaign_channel_date', 'channel', 'date'),
        Index('idx_campaign_funnel_date', 'funnel_stage', 'date'),
    )
    
    def __repr__(self):
        return f"<Campaign(id={self.id}, campaign_id='{self.campaign_id}', name='{self.campaign_name}')>"


class Analysis(Base):
    """Analysis results model."""
    __tablename__ = 'analyses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(String(255), unique=True, nullable=False, index=True)
    campaign_id = Column(Integer, ForeignKey('campaigns.id'), nullable=False)
    
    # Analysis type
    analysis_type = Column(String(50), nullable=False)  # 'auto', 'rag', 'channel', 'pattern'
    
    # Results stored as JSON
    insights = Column(JSON)
    recommendations = Column(JSON)
    metrics = Column(JSON)
    executive_summary = Column(JSON)
    
    # Metadata
    status = Column(String(50), default='pending')  # pending, completed, failed
    error_message = Column(Text)
    execution_time = Column(Float)  # seconds
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="analyses")
    
    # Indexes
    __table_args__ = (
        Index('idx_analysis_type_created', 'analysis_type', 'created_at'),
        Index('idx_analysis_status', 'status'),
        Index('idx_analysis_campaign_id', 'campaign_id'),
    )
    
    def __repr__(self):
        return f"<Analysis(id={self.id}, analysis_id='{self.analysis_id}', type='{self.analysis_type}')>"


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


class CampaignContext(Base):
    """Store campaign context for better analysis."""
    __tablename__ = 'campaign_contexts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(Integer, ForeignKey('campaigns.id'), nullable=False, unique=True, index=True)
    
    # Business context
    business_model = Column(String(50))  # 'B2B', 'B2C', 'B2B2C'
    industry = Column(String(100))
    target_audience = Column(Text)
    
    # Goals and benchmarks
    goals = Column(JSON)
    benchmarks = Column(JSON)
    
    # Historical performance
    historical_metrics = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<CampaignContext(id={self.id}, campaign_id={self.campaign_id})>"
