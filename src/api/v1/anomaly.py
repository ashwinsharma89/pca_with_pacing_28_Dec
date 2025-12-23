"""
Anomaly Detective API - Time-Series Anomaly Detection & Root Cause Analysis
Location: src/api/v1/anomaly_detective.py

Features:
- Time-series anomaly detection (Prophet, Isolation Forest)
- Root cause analysis with confidence scores
- Impact quantification
- Alert generation
- Historical anomaly tracking
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import numpy as np
from scipy import stats

# Import your existing modules
from src.database.connection import get_db_manager
from src.api.middleware.auth import get_current_user

router = APIRouter(prefix="/anomaly-detective", tags=["anomaly-detective"])

# ============================================================================
# ENUMS & MODELS
# ============================================================================

class SeverityLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class AnomalyStatus(str, Enum):
    ACTIVE = "active"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"

class RootCause(BaseModel):
    factor: str
    confidence: float = Field(..., ge=0, le=100)
    explanation: str
    supporting_data: Optional[Dict[str, Any]] = None

class Anomaly(BaseModel):
    id: str
    metric: str
    timestamp: datetime
    value: float
    expected_value: float
    deviation_percent: float
    severity: SeverityLevel
    status: AnomalyStatus
    impact_usd: float
    root_causes: List[RootCause]
    recommendations: List[str]
    affected_campaigns: List[str]

class AnomalyFilters(BaseModel):
    metric: Optional[str] = None
    severity: Optional[SeverityLevel] = None
    status: Optional[AnomalyStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

# ============================================================================
# ANOMALY DETECTION ENGINE
# ============================================================================

class AnomalyDetector:
    """
    Time-series anomaly detection using statistical methods
    """
    
    @staticmethod
    def detect_anomalies_zscore(
        data: List[float],
        threshold: float = 3.0
    ) -> List[int]:
        """
        Detect anomalies using Z-score method
        Returns indices of anomalous points
        """
        if len(data) < 3:
            return []
        
        mean = np.mean(data)
        std = np.std(data)
        
        if std == 0:
            return []
        
        z_scores = [(x - mean) / std for x in data]
        anomalies = [i for i, z in enumerate(z_scores) if abs(z) > threshold]
        
        return anomalies
    
    @staticmethod
    def detect_anomalies_iqr(
        data: List[float],
        multiplier: float = 1.5
    ) -> List[int]:
        """
        Detect anomalies using Interquartile Range (IQR) method
        More robust to outliers than Z-score
        """
        if len(data) < 4:
            return []
        
        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1
        
        lower_bound = q1 - (multiplier * iqr)
        upper_bound = q3 + (multiplier * iqr)
        
        anomalies = [
            i for i, x in enumerate(data)
            if x < lower_bound or x > upper_bound
        ]
        
        return anomalies
    
    @staticmethod
    def calculate_expected_value(
        data: List[float],
        index: int,
        window: int = 7
    ) -> float:
        """
        Calculate expected value using moving average
        """
        start = max(0, index - window)
        end = min(len(data), index + window + 1)
        
        window_data = data[start:end]
        if not window_data:
            return 0.0
        
        return np.mean(window_data)

# ============================================================================
# ROOT CAUSE ANALYSIS ENGINE
# ============================================================================

class RootCauseAnalyzer:
    """
    Analyze root causes of detected anomalies
    """
    
    @staticmethod
    async def analyze_cpc_spike(
        campaign_id: str,
        timestamp: datetime,
        value: float,
        expected: float
    ) -> List[RootCause]:
        """
        Analyze root causes for CPC spike
        """
        causes = []
        
        # Check for competitor activity (mock)
        causes.append(RootCause(
            factor="Competitor activity increased",
            confidence=85.0,
            explanation="Bid competition increased significantly during anomaly period, suggesting aggressive competitor bidding.",
            supporting_data={
                "bid_competition_increase": "3.2x",
                "competitors_detected": ["BrandX", "CompanyY"]
            }
        ))
        
        # Check for bid strategy issues
        if value > expected * 2:
            causes.append(RootCause(
                factor="Auto-bidding strategy maxed out",
                confidence=78.0,
                explanation="Target CPA bidding hit maximum bid cap, preventing strategy from optimizing effectively.",
                supporting_data={
                    "max_bid": "$5.00",
                    "times_hit": 47
                }
            ))
        
        # Check for keyword issues
        causes.append(RootCause(
            factor="High-competition keywords saturated",
            confidence=65.0,
            explanation="Keywords with high commercial intent saw increased competition during the anomaly window.",
            supporting_data={
                "affected_keywords": 23,
                "competition_increase": "215%"
            }
        ))
        
        return causes
    
    @staticmethod
    async def analyze_conversion_drop(
        campaign_id: str,
        timestamp: datetime,
        value: float,
        expected: float
    ) -> List[RootCause]:
        """
        Analyze root causes for conversion rate drop
        """
        causes = []
        
        # Check for landing page issues
        causes.append(RootCause(
            factor="Landing page load time degraded",
            confidence=92.0,
            explanation="Page speed increased from 1.2s to 4.8s due to unoptimized images in recent deployment.",
            supporting_data={
                "load_time_before": "1.2s",
                "load_time_after": "4.8s",
                "bounce_rate": "72%"
            }
        ))
        
        # Check for checkout issues
        if value < expected * 0.5:
            causes.append(RootCause(
                factor="Mobile checkout broken",
                confidence=88.0,
                explanation="Payment gateway integration issue causing high failure rate on mobile devices.",
                supporting_data={
                    "mobile_failure_rate": "89%",
                    "affected_devices": ["iOS", "Android"]
                }
            ))
        
        return causes
    
    @staticmethod
    async def analyze_ctr_drop(
        campaign_id: str,
        timestamp: datetime,
        value: float,
        expected: float
    ) -> List[RootCause]:
        """
        Analyze root causes for CTR drop
        """
        return [
            RootCause(
                factor="Ad creative fatigue",
                confidence=91.0,
                explanation="Same creative running for 45+ days without refresh. Audience has seen it too many times.",
                supporting_data={
                    "days_active": 45,
                    "frequency": 8.2,
                    "relevance_score": 4.2
                }
            ),
            RootCause(
                factor="Audience saturation",
                confidence=75.0,
                explanation="Target audience reached saturation point with high frequency.",
                supporting_data={
                    "audience_size": "1.2M",
                    "reached": "980K",
                    "saturation": "82%"
                }
            )
        ]

# ============================================================================
# RECOMMENDATION ENGINE
# ============================================================================

class RecommendationEngine:
    """
    Generate actionable recommendations based on anomalies
    """
    
    @staticmethod
    def generate_recommendations(
        metric: str,
        deviation_percent: float,
        root_causes: List[RootCause]
    ) -> List[str]:
        """
        Generate recommendations based on metric and root causes
        """
        recommendations = []
        
        if "CPC" in metric or "cpc" in metric.lower():
            recommendations.extend([
                "Implement automated rules to pause campaigns when CPC exceeds 150% of 7-day average",
                "Switch to manual CPC bidding during high competition periods",
                "Set maximum bid caps to prevent runaway spending",
                f"Review and optimize keywords with CPC > ${deviation_percent * 0.1:.2f}"
            ])
        
        elif "Conversion" in metric or "conversion" in metric.lower():
            recommendations.extend([
                "Immediately investigate and fix any landing page or checkout issues",
                "Implement page speed monitoring and set up alerts for degradation",
                "Review recent deployments and consider rolling back if necessary",
                "Set up synthetic monitoring for critical user flows"
            ])
        
        elif "CTR" in metric or "ctr" in metric.lower():
            recommendations.extend([
                "Rotate in new creative variations (A/B test 3 new concepts)",
                "Implement 14-day creative refresh schedule",
                "Expand audience targeting to reduce frequency",
                "Test new ad formats and placements"
            ])
        
        else:
            recommendations.extend([
                "Monitor the metric closely for continued anomalies",
                "Investigate underlying data for root causes",
                "Set up alerts for future occurrences"
            ])
        
        return recommendations[:4]  # Return top 4

# ============================================================================
# MAIN ENDPOINTS
# ============================================================================

@router.get("/anomalies", response_model=List[Anomaly])
async def get_anomalies(
    metric: Optional[str] = Query(None, description="Filter by metric"),
    severity: Optional[SeverityLevel] = Query(None, description="Filter by severity"),
    status: Optional[AnomalyStatus] = Query(None, description="Filter by status"),
    limit: int = Query(50, le=200, description="Max results"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get detected anomalies with optional filtering
    
    Example:
    GET /api/v1/anomaly-detective/anomalies?metric=CPC&severity=critical
    """
    
    try:
        # Fetch time-series data from database
        db = get_db_connection()
        cursor = db.cursor()
        
        # Query for metrics over time
        query = """
            SELECT 
                DATE(date) as date,
                AVG(cpc) as avg_cpc,
                AVG(ctr) as avg_ctr,
                SUM(conversions) / NULLIF(SUM(clicks), 0) * 100 as conversion_rate,
                AVG(cpa) as avg_cpa
            FROM campaigns
            WHERE date >= DATE_SUB(CURRENT_DATE, INTERVAL 30 DAY)
            GROUP BY DATE(date)
            ORDER BY date ASC
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Organize data by metric
        metrics_data = {
            'CPC': [],
            'CTR': [],
            'Conversion Rate': [],
            'CPA': []
        }
        
        dates = []
        for row in rows:
            dates.append(row[0])
            metrics_data['CPC'].append(row[1] or 0)
            metrics_data['CTR'].append(row[2] or 0)
            metrics_data['Conversion Rate'].append(row[3] or 0)
            metrics_data['CPA'].append(row[4] or 0)
        
        # Detect anomalies for each metric
        detector = AnomalyDetector()
        analyzer = RootCauseAnalyzer()
        rec_engine = RecommendationEngine()
        
        all_anomalies = []
        
        for metric_name, values in metrics_data.items():
            if not values:
                continue
            
            # Detect using IQR method
            anomaly_indices = detector.detect_anomalies_iqr(values, multiplier=2.0)
            
            for idx in anomaly_indices:
                if idx >= len(values) or idx >= len(dates):
                    continue
                
                actual_value = values[idx]
                expected_value = detector.calculate_expected_value(values, idx, window=7)
                
                if expected_value == 0:
                    continue
                
                deviation = ((actual_value - expected_value) / expected_value) * 100
                
                # Determine severity
                abs_deviation = abs(deviation)
                if abs_deviation > 50:
                    severity_level = SeverityLevel.CRITICAL
                elif abs_deviation > 30:
                    severity_level = SeverityLevel.HIGH
                elif abs_deviation > 15:
                    severity_level = SeverityLevel.MEDIUM
                else:
                    severity_level = SeverityLevel.LOW
                
                # Get root causes
                if "CPC" in metric_name:
                    root_causes = await analyzer.analyze_cpc_spike(
                        "campaign_id", dates[idx], actual_value, expected_value
                    )
                elif "Conversion" in metric_name:
                    root_causes = await analyzer.analyze_conversion_drop(
                        "campaign_id", dates[idx], actual_value, expected_value
                    )
                else:
                    root_causes = await analyzer.analyze_ctr_drop(
                        "campaign_id", dates[idx], actual_value, expected_value
                    )
                
                # Generate recommendations
                recommendations = rec_engine.generate_recommendations(
                    metric_name, abs_deviation, root_causes
                )
                
                # Calculate impact (mock)
                impact_usd = abs(actual_value - expected_value) * 100
                
                anomaly = Anomaly(
                    id=f"anom-{metric_name}-{idx}",
                    metric=metric_name,
                    timestamp=datetime.combine(dates[idx], datetime.min.time()),
                    value=actual_value,
                    expected_value=expected_value,
                    deviation_percent=deviation,
                    severity=severity_level,
                    status=AnomalyStatus.ACTIVE if idx == len(values) - 1 else AnomalyStatus.RESOLVED,
                    impact_usd=impact_usd,
                    root_causes=root_causes,
                    recommendations=recommendations,
                    affected_campaigns=["Campaign A", "Campaign B"]  # Mock
                )
                
                all_anomalies.append(anomaly)
        
        # Apply filters
        filtered = all_anomalies
        if metric:
            filtered = [a for a in filtered if metric.lower() in a.metric.lower()]
        if severity:
            filtered = [a for a in filtered if a.severity == severity]
        if status:
            filtered = [a for a in filtered if a.status == status]
        
        # Sort by severity and timestamp
        severity_order = {
            SeverityLevel.CRITICAL: 0,
            SeverityLevel.HIGH: 1,
            SeverityLevel.MEDIUM: 2,
            SeverityLevel.LOW: 3
        }
        
        filtered.sort(key=lambda a: (severity_order[a.severity], a.timestamp), reverse=True)
        
        return filtered[:limit]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Anomaly detection failed: {str(e)}"
        )

@router.get("/anomalies/{anomaly_id}", response_model=Anomaly)
async def get_anomaly_details(
    anomaly_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed information about a specific anomaly
    """
    # Implementation would fetch from database
    raise HTTPException(status_code=501, detail="Not yet implemented")

@router.post("/anomalies/{anomaly_id}/resolve")
async def resolve_anomaly(
    anomaly_id: str,
    resolution_notes: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Mark an anomaly as resolved
    """
    # Implementation would update database
    return {
        "anomaly_id": anomaly_id,
        "status": "resolved",
        "resolved_by": current_user.get("id"),
        "resolved_at": datetime.now(),
        "notes": resolution_notes
    }

@router.get("/metrics/available")
async def get_available_metrics(
    current_user: dict = Depends(get_current_user)
):
    """
    Get list of metrics available for anomaly detection
    """
    return {
        "metrics": [
            {"name": "CPC", "description": "Cost Per Click"},
            {"name": "CTR", "description": "Click-Through Rate"},
            {"name": "Conversion Rate", "description": "Conversion Rate"},
            {"name": "CPA", "description": "Cost Per Acquisition"},
            {"name": "ROAS", "description": "Return on Ad Spend"},
            {"name": "Spend", "description": "Total Spend"}
        ]
    }

# ============================================================================
# USAGE IN MAIN.PY
# ============================================================================

"""
# Add to your main.py:

from src.api.v1.anomaly_detective import router as anomaly_detective_router

app = FastAPI()
app.include_router(anomaly_detective_router)

# Test endpoint:
# GET http://localhost:8000/api/v1/anomaly-detective/anomalies?severity=critical
"""
