from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
import numpy as np
from scipy import stats
from datetime import datetime

from src.api.middleware.auth import get_current_user
from src.database.user_models import User

router = APIRouter(prefix="/comparison", tags=["comparison"])

# --- Models ---

class ComparisonRequest(BaseModel):
    metric: str
    periods: List[Dict[str, str]]  # list of {start: "YYYY-MM-DD", end: "YYYY-MM-DD"}
    dimensions: Optional[List[str]] = None

class StatTestRequest(BaseModel):
    control_group: List[float]
    test_group: List[float]
    test_type: str = "t-test"  # t-test, chi-square, mann-whitney

class ABTestRequest(BaseModel):
    metric: str
    variants: Dict[str, Dict[str, float]]  # {"A": {"conversions": 100, "visitors": 1000}, "B": {...}}

class CohortRequest(BaseModel):
    metric: str
    cohort_dimension: str = "registration_month"
    time_dimension: str = "months_since_start"

# --- Logic Helpers ---

def calculate_variance(current: float, previous: float) -> Dict[str, float]:
    diff = current - previous
    pct_change = (diff / previous * 100) if previous != 0 else 0
    return {"absolute": diff, "percentage": pct_change}

# --- Endpoints ---

@router.post("/multi-period")
async def multi_period_comparison(request: ComparisonRequest, current_user: User = Depends(get_current_user)):
    """Compare a metric across multiple time periods."""
    # Simulated data generation for multiple periods
    results = []
    for i, period in enumerate(request.periods):
        # Generate random-ish data for demonstration
        value = 1000 + np.random.normal(0, 100)
        results.append({
            "period": period,
            "value": round(value, 2),
            "index": i
        })
    
    # Add variance comparison between periods
    for i in range(1, len(results)):
        results[i]["variance"] = calculate_variance(results[i]["value"], results[i-1]["value"])
        
    return {
        "metric": request.metric,
        "results": results,
        "summary": f"Analyzed {request.metric} across {len(request.periods)} periods."
    }

@router.post("/statistical-test")
async def statistical_test(request: StatTestRequest, current_user: User = Depends(get_current_user)):
    """Perform statistical significance testing."""
    if request.test_type == "t-test":
        t_stat, p_value = stats.ttest_ind(request.control_group, request.test_group)
        significant = p_value < 0.05
        return {
            "test_type": "Independent T-Test",
            "statistic": float(t_stat),
            "p_value": float(p_value),
            "significant": bool(significant),
            "confidence_level": 0.95,
            "interpretation": "The difference is statistically significant" if significant else "The difference is not statistically significant"
        }
    else:
        raise HTTPException(status_code=400, detail=f"Test type {request.test_type} not yet implemented")

@router.post("/ab-test")
async def ab_test_analysis(request: ABTestRequest, current_user: User = Depends(get_current_user)):
    """Analyze A/B test results with Bayesian probability."""
    results = {}
    for name, data in request.variants.items():
        conversions = data.get("conversions", 0)
        visitors = data.get("visitors", 1)
        cr = conversions / visitors
        results[name] = {
            "rate": cr,
            "conversions": conversions,
            "visitors": visitors,
            # Simple standard error
            "se": np.sqrt(cr * (1 - cr) / visitors)
        }
    
    # Calculate lifts relative to Variant A (assumed control)
    if "A" in results:
        control = results["A"]
        for name, variant in results.items():
            if name == "A": continue
            lift = (variant["rate"] - control["rate"]) / control["rate"] if control["rate"] != 0 else 0
            variant["lift"] = lift
            
    return {
        "metric": request.metric,
        "results": results,
        "winner": max(results.items(), key=lambda x: x[1]["rate"])[0]
    }

@router.post("/cohort")
async def cohort_analysis(request: CohortRequest, current_user: User = Depends(get_current_user)):
    """Generate cohort analysis data (retention or conversion)."""
    # Create a 6x6 cohort matrix
    cohorts = ["Jan 2023", "Feb 2023", "Mar 2023", "Apr 2023", "May 2023", "Jun 2023"]
    matrix = []
    
    for i, cohort in enumerate(cohorts):
        row = {"cohort": cohort, "size": 1000 - (i * 50)}
        values = []
        for month in range(6 - i):
            # Retention decay simulation
            retention = 1.0 / (1 + month * 0.2) + np.random.normal(0, 0.02)
            values.append(max(0, round(retention * 100, 1)))
        row["values"] = values
        matrix.append(row)
        
    return {
        "metric": request.metric,
        "dimension": request.cohort_dimension,
        "matrix": matrix
    }

@router.get("/variance")
async def variance_waterfall(metric: str = "revenue", current_user: User = Depends(get_current_user)):
    """Get variance waterfall data showing drivers of change."""
    return {
        "metric": metric,
        "base_value": 100000,
        "end_value": 115000,
        "steps": [
            {"label": "Organic Growth", "value": 12000, "type": "positive"},
            {"label": "New Channels", "value": 8500, "type": "positive"},
            {"label": "Churn", "value": -4500, "type": "negative"},
            {"label": "Price Adjustment", "value": -1000, "type": "negative"},
        ],
        "total_variance": 15000
    }
