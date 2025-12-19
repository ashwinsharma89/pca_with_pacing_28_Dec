import bleach
from pydantic import BaseModel, Field, validator
from typing import Optional, List

def sanitize_string(v: str) -> str:
    if not v:
        return v
    return bleach.clean(v, tags=[], strip=True)

class ChatRequest(BaseModel):
    question: str
    knowledge_mode: bool = False  # If True, use RAG knowledge base instead of SQL
    use_rag_context: bool = True  # Add RAG context to enhance SQL answers

    @validator('question')
    def sanitize_question(cls, v):
        return sanitize_string(v)

class GlobalAnalysisRequest(BaseModel):
    use_rag_summary: bool = True
    include_recommendations: bool = True
    include_benchmarks: bool = True
    analysis_depth: Optional[str] = "deep"

    @validator('analysis_depth')
    def sanitize_depth(cls, v):
        if v: return sanitize_string(v)
        return v

class KPIComparisonRequest(BaseModel):
    kpis: List[str]
    dimension: str = "platform"
    platforms: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    normalize: bool = False

    @validator('dimension', 'platforms', 'start_date', 'end_date')
    def sanitize_strings(cls, v):
        if v: return sanitize_string(v)
        return v
