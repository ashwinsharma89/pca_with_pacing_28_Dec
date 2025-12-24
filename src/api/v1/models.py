import bleach
from pydantic import BaseModel, Field, validator, field_validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
import re

def sanitize_string(v: str) -> str:
    if not v:
        return v
    return bleach.clean(v, tags=[], strip=True)

# ============================================================================
# SHARED BASE MODELS
# ============================================================================

class PaginationRequest(BaseModel):
    """Base model for pagination parameters"""
    limit: int = Field(default=100, ge=1, le=1000, description="Max items per page")
    offset: int = Field(default=0, ge=0, description="Number of items to skip")

class DateRangeRequest(BaseModel):
    """Base model for date range filtering"""
    start_date: Optional[date] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[date] = Field(None, description="End date (YYYY-MM-DD)")
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        if v and 'start_date' in values and values['start_date']:
            if v < values['start_date']:
                raise ValueError('end_date must be after or equal to start_date')
        return v

# ============================================================================
# FILE UPLOAD VALIDATION
# ============================================================================

class FileUploadRequest(BaseModel):
    """Validation for file upload parameters"""
    sheet_name: Optional[str] = Field(None, max_length=255, description="Excel sheet name")
    file_size_bytes: Optional[int] = Field(None, le=104857600, description="Max 100MB")
    file_extension: str = Field(..., regex=r'^(csv|xlsx|xls)$', description="Allowed: csv, xlsx, xls")
    
    @validator('sheet_name')
    def sanitize_sheet_name(cls, v):
        if v:
            return sanitize_string(v)
        return v

class PreviewSheetsRequest(BaseModel):
    """Validation for Excel sheet preview"""
    file_size_bytes: Optional[int] = Field(None, le=104857600, description="Max 100MB")

# ============================================================================
# FILTER VALIDATION
# ============================================================================

class CampaignFilterRequest(BaseModel):
    """Validation for campaign filtering parameters"""
    platforms: Optional[List[str]] = Field(None, max_items=50, description="Max 50 platforms")
    channels: Optional[List[str]] = Field(None, max_items=50, description="Max 50 channels")
    funnels: Optional[List[str]] = Field(None, max_items=20, description="Max 20 funnel stages")
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    min_spend: Optional[float] = Field(None, ge=0, description="Minimum spend filter")
    max_spend: Optional[float] = Field(None, ge=0, description="Maximum spend filter")
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        if v and 'start_date' in values and values['start_date']:
            if v < values['start_date']:
                raise ValueError('end_date must be after start_date')
        return v
    
    @validator('max_spend')
    def validate_spend_range(cls, v, values):
        if v and 'min_spend' in values and values['min_spend']:
            if v < values['min_spend']:
                raise ValueError('max_spend must be greater than min_spend')
        return v
    
    @validator('platforms', 'channels', 'funnels')
    def sanitize_lists(cls, v):
        if v:
            return [sanitize_string(item) for item in v]
        return v

# ============================================================================
# WEBHOOK VALIDATION
# ============================================================================

class WebhookPayloadRequest(BaseModel):
    """Validation for webhook payload data"""
    event_type: str = Field(..., regex=r'^[a-z_]+$', max_length=100, description="Event type (lowercase, underscores)")
    data: Dict[str, Any] = Field(..., description="Event data payload")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    source: Optional[str] = Field(None, max_length=255, description="Event source")
    
    @validator('event_type')
    def sanitize_event_type(cls, v):
        return sanitize_string(v)
    
    @validator('source')
    def sanitize_source(cls, v):
        if v:
            return sanitize_string(v)
        return v

# ============================================================================
# EXISTING MODELS (Enhanced)
# ============================================================================

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000, description="User question")
    knowledge_mode: bool = Field(default=False, description="Use RAG knowledge base instead of SQL")
    use_rag_context: bool = Field(default=True, description="Add RAG context to enhance SQL answers")

    @validator('question')
    def sanitize_question(cls, v):
        return sanitize_string(v)

class GlobalAnalysisRequest(BaseModel):
    use_rag_summary: bool = Field(default=True, description="Include RAG-generated summary")
    include_recommendations: bool = Field(default=True, description="Include AI recommendations")
    include_benchmarks: bool = Field(default=True, description="Include industry benchmarks")
    analysis_depth: Optional[str] = Field(default="deep", regex=r'^(quick|standard|deep)$', description="Analysis depth level")

    @validator('analysis_depth')
    def sanitize_depth(cls, v):
        if v: return sanitize_string(v)
        return v

class KPIComparisonRequest(BaseModel):
    kpis: List[str] = Field(..., min_items=1, max_items=20, description="KPIs to compare (max 20)")
    dimension: str = Field(default="platform", regex=r'^[a-z_]+$', description="Dimension to compare by")
    platforms: Optional[str] = Field(None, max_length=500, description="Comma-separated platforms")
    start_date: Optional[str] = Field(None, regex=r'^\d{4}-\d{2}-\d{2}$', description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, regex=r'^\d{4}-\d{2}-\d{2}$', description="End date (YYYY-MM-DD)")
    normalize: bool = Field(default=False, description="Normalize values for comparison")

    @validator('dimension', 'platforms', 'start_date', 'end_date')
    def sanitize_strings(cls, v):
        if v: return sanitize_string(v)
        return v
    
    @validator('kpis')
    def sanitize_kpis(cls, v):
        return [sanitize_string(kpi) for kpi in v]
