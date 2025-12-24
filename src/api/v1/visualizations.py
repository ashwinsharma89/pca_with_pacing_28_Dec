from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import random

from src.api.middleware.auth import get_current_user
from src.database.user_models import User

router = APIRouter(prefix="/visualizations", tags=["visualizations"])

# --- Models ---

class RecommendationRequest(BaseModel):
    data_summary: Dict[str, Any]
    intent: Optional[str] = None  # 'comparison', 'distribution', 'trend', 'composition'

class VisualizationDataRequest(BaseModel):
    metric: str
    dimension: str
    filters: Optional[Dict[str, Any]] = None

class SankeyRequest(BaseModel):
    source_layer: str  # e.g., 'channel'
    target_layer: str  # e.g., 'conversion_type'
    metric: str = 'conversions'

# --- Endpoints ---

@router.post("/recommend")
async def recommend_chart(request: RecommendationRequest, current_user: User = Depends(get_current_user)):
    """Recommend the best chart type based on data characteristics."""
    dims = request.data_summary.get("dimensions", 0)
    metrics = request.data_summary.get("metrics", 0)
    has_time = request.data_summary.get("has_time", False)
    
    recommendation = {
        "chart_type": "bar",
        "confidence": 0.8,
        "reason": "Defaulting to bar chart for categorical comparison."
    }
    
    if has_time:
        recommendation = {
            "chart_type": "line",
            "confidence": 0.95,
            "reason": "Line charts are best for showing trends over time."
        }
    elif dims == 1 and metrics == 1:
        recommendation = {
            "chart_type": "pie",
            "confidence": 0.7,
            "reason": "Pie charts work well for single dimension compositions."
        }
    elif metrics > 1:
        recommendation = {
            "chart_type": "radar",
            "confidence": 0.6,
            "reason": "Radar charts are useful for multi-metric comparison."
        }
        
    return {
        "recommended": recommendation,
        "alternatives": ["bar", "table", "scatter"]
    }

@router.post("/data")
async def get_visualization_data(request: VisualizationDataRequest, current_user: User = Depends(get_current_user)):
    """Get processed data optimized for visualization components."""
    # Simulated data generation
    labels = ["Category A", "Category B", "Category C", "Category D", "Category E"]
    data = [random.randint(100, 1000) for _ in range(5)]  # nosec B311
    
    return {
        "metric": request.metric,
        "dimension": request.dimension,
        "chart_data": [
            {"name": label, "value": value} for label, value in zip(labels, data)
        ]
    }

@router.get("/palettes")
async def get_color_palettes():
    """Get system-defined color palettes for consistent branding."""
    return [
        {
            "id": "vibrant",
            "name": "Vibrant PCA",
            "colors": ["#6366f1", "#8b5cf6", "#d946ef", "#f43f5e", "#f59e0b"]
        },
        {
            "id": "monochrome",
            "name": "Professional Indigo",
            "colors": ["#312e81", "#3730a3", "#4338ca", "#4f46e5", "#6366f1"]
        },
        {
            "id": "status",
            "name": "Status Semantic",
            "colors": ["#22c55e", "#f59e0b", "#ef4444", "#3b82f6", "#64748b"]
        }
    ]

@router.post("/sankey")
async def get_sankey_data(request: SankeyRequest, current_user: User = Depends(get_current_user)):
    """Get flow data for Sankey diagrams."""
    nodes = [
        {"name": "Google Ads"}, {"name": "Facebook Ads"}, {"name": "Email"},
        {"name": "Landing Page"}, {"name": "Product Page"},
        {"name": "Checkout"}, {"name": "Purchase"}
    ]
    
    links = [
        {"source": 0, "target": 3, "value": 1500},
        {"source": 1, "target": 3, "value": 1200},
        {"source": 2, "target": 4, "value": 800},
        {"source": 3, "target": 4, "value": 2000},
        {"source": 4, "target": 5, "value": 1000},
        {"source": 5, "target": 6, "value": 450}
    ]
    
    return {
        "nodes": nodes,
        "links": links,
        "layers": [request.source_layer, "intermediate", request.target_layer]
    }
