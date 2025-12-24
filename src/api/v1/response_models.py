"""
Response Models for API Validation

Ensures consistent response structure and prevents data leakage.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============================================================================
# STANDARD RESPONSE WRAPPERS
# ============================================================================

class SuccessResponse(BaseModel):
    """Standard success response"""
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error: Dict[str, Any] = Field(..., description="Error details")
    path: Optional[str] = None
    method: Optional[str] = None


class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    success: bool = True
    data: List[Dict[str, Any]]
    total: int = Field(..., description="Total number of items")
    limit: int = Field(..., description="Items per page")
    offset: int = Field(..., description="Current offset")
    has_more: bool = Field(..., description="Whether more items exist")


# ============================================================================
# CAMPAIGN RESPONSES
# ============================================================================

class CampaignUploadResponse(BaseModel):
    """Response for campaign data upload"""
    success: bool = True
    message: str
    rows_imported: int = Field(..., ge=0, description="Number of rows imported")
    file_size_mb: float = Field(..., ge=0, description="File size in MB")
    processing_time_seconds: float = Field(..., ge=0, description="Processing time")
    parquet_path: str = Field(..., description="Path to stored Parquet file")


class ChatResponse(BaseModel):
    """Response for chat/Q&A queries"""
    success: bool
    query: Optional[str] = None
    sql: Optional[str] = None
    results: Optional[List[Dict[str, Any]]] = None
    data: Optional[List[Dict[str, Any]]] = None
    summary: Optional[str] = None
    chart: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    knowledge: Optional[Dict[str, Any]] = None
    retrieved: Optional[List[Dict[str, Any]]] = Field(default_factory=list)


class AnalysisResponse(BaseModel):
    """Response for campaign analysis"""
    success: bool = True
    insights: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    summary: Optional[str] = None
    benchmarks: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


# ============================================================================
# AUTH RESPONSES
# ============================================================================

class LoginResponse(BaseModel):
    """Response for login"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Token expiry in seconds")
    user: Dict[str, Any] = Field(..., description="User information")
    requires_mfa: Optional[bool] = False


class MFASetupResponse(BaseModel):
    """Response for MFA setup"""
    secret: str = Field(..., description="MFA secret key")
    qr_code: str = Field(..., description="QR code for authenticator app")
    backup_codes: List[str] = Field(..., description="Backup recovery codes")


# ============================================================================
# WEBHOOK RESPONSES
# ============================================================================

class WebhookResponse(BaseModel):
    """Response for webhook operations"""
    id: str
    url: str
    events: List[str]
    description: Optional[str]
    is_active: bool
    created_at: datetime
    last_triggered_at: Optional[datetime]
    success_count: int = Field(..., ge=0)
    failure_count: int = Field(..., ge=0)


# ============================================================================
# VALIDATION ERROR RESPONSE
# ============================================================================

class ValidationErrorDetail(BaseModel):
    """Detail for a single validation error"""
    loc: List[str] = Field(..., description="Location of error (field path)")
    msg: str = Field(..., description="Error message")
    type: str = Field(..., description="Error type")


class ValidationErrorResponse(BaseModel):
    """Response for validation errors"""
    success: bool = False
    error: Dict[str, Any] = Field(
        ...,
        description="Validation error details",
        example={
            "code": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": []
        }
    )
    detail: List[ValidationErrorDetail] = Field(..., description="Detailed validation errors")
