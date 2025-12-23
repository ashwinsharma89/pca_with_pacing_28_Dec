"""
Real-Time Command Center API Endpoint
Provides real-time campaign monitoring with WebSocket streaming
"""

from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy import text
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio
import json
from loguru import logger

from src.api.middleware.auth import get_current_user
from src.database.user_models import User
from src.database.connection import get_db_manager

router = APIRouter(prefix="/realtime", tags=["realtime"])


class MetricUpdate(BaseModel):
    current: float
    previous: float
    change_percent: float
    trend: str  # "up", "down", "stable"


class CampaignStatus(BaseModel):
    id: str
    name: str
    platform: str
    status: str  # "active", "paused", "warning", "critical"
    spend_today: float
    daily_budget: float
    pacing_percent: float
    cpa: float
    conversions: int
    last_update: str


class Alert(BaseModel):
    id: str
    timestamp: str
    severity: str  # "info", "warning", "critical"
    message: str
    campaign: Optional[str] = None
    metric: Optional[str] = None


class MetricsSnapshot(BaseModel):
    type: str = "metrics_update"
    timestamp: str
    metrics: Dict[str, MetricUpdate]
    campaigns: List[CampaignStatus]
    alerts: List[Alert]


@router.get("/snapshot", response_model=MetricsSnapshot)
async def get_realtime_snapshot(
    current_user: User = Depends(get_current_user)
):
    """
    Get current real-time metrics snapshot
    
    Returns:
    - Current metrics (spend, conversions, CPA, CTR)
    - Active campaign statuses
    - Recent alerts
    """
    try:
        username = current_user.get('username') if isinstance(current_user, dict) else getattr(current_user, 'username', 'unknown')
        logger.info(f"Fetching real-time snapshot for user {username}")
        
        db_manager = get_db_manager()
        
        # Get today's data
        query = """
        SELECT 
            id as campaign_id,
            name as campaign_name,
            platform,
            date,
            spend,
            impressions,
            clicks,
            conversions,
            cpc,
            cpa,
            ctr,
            roas,
            budget
        FROM campaigns
        WHERE date = date('now')
        ORDER BY spend DESC
        """
        
        with db_manager.get_session() as session:
            result = session.execute(text(query))
            today_campaigns = [dict(r) for r in result.mappings().all()]
        
        # Get yesterday's data for comparison
        yesterday_query = """
        SELECT 
            SUM(spend) as total_spend,
            SUM(conversions) as total_conversions,
            AVG(cpa) as avg_cpa,
            AVG(ctr) as avg_ctr
        FROM campaigns
        WHERE date = date('now', '-1 day')
        """
        
        with db_manager.get_session() as session:
            result = session.execute(text(yesterday_query))
            yesterday_data = result.mappings().first()
            yesterday = dict(yesterday_data) if yesterday_data else {}
        
        # Calculate current metrics
        total_spend = sum(c.get('spend', 0) for c in today_campaigns)
        total_conversions = sum(c.get('conversions', 0) for c in today_campaigns)
        avg_cpa = sum(c.get('cpa', 0) for c in today_campaigns) / len(today_campaigns) if today_campaigns else 0
        avg_ctr = sum(c.get('ctr', 0) for c in today_campaigns) / len(today_campaigns) if today_campaigns else 0
        
        # Calculate changes
        prev_spend = yesterday.get('total_spend', total_spend * 0.95)
        prev_conversions = yesterday.get('total_conversions', total_conversions * 0.92)
        prev_cpa = yesterday.get('avg_cpa', avg_cpa * 1.05)
        prev_ctr = yesterday.get('avg_ctr', avg_ctr * 0.98)
        
        metrics = {
            "spend": MetricUpdate(
                current=round(total_spend, 2),
                previous=round(prev_spend, 2),
                change_percent=round(((total_spend - prev_spend) / prev_spend * 100) if prev_spend > 0 else 0, 1),
                trend="up" if total_spend > prev_spend else "down"
            ),
            "conversions": MetricUpdate(
                current=total_conversions,
                previous=prev_conversions,
                change_percent=round(((total_conversions - prev_conversions) / prev_conversions * 100) if prev_conversions > 0 else 0, 1),
                trend="up" if total_conversions > prev_conversions else "down"
            ),
            "cpa": MetricUpdate(
                current=round(avg_cpa, 2),
                previous=round(prev_cpa, 2),
                change_percent=round(((avg_cpa - prev_cpa) / prev_cpa * 100) if prev_cpa > 0 else 0, 1),
                trend="down" if avg_cpa < prev_cpa else "up"
            ),
            "ctr": MetricUpdate(
                current=round(avg_ctr, 2),
                previous=round(prev_ctr, 2),
                change_percent=round(((avg_ctr - prev_ctr) / prev_ctr * 100) if prev_ctr > 0 else 0, 1),
                trend="up" if avg_ctr > prev_ctr else "down"
            )
        }
        
        # Build campaign statuses
        campaigns = []
        for campaign in today_campaigns[:10]:  # Top 10 campaigns
            spend_today = campaign.get('spend', 0)
            budget = campaign.get('budget', spend_today * 1.2)
            pacing = (spend_today / budget * 100) if budget > 0 else 0
            
            # Determine status
            if pacing > 110:
                status = "critical"
            elif pacing > 90:
                status = "warning"
            elif campaign.get('status', 'active') == 'paused':
                status = "paused"
            else:
                status = "active"
            
            campaigns.append(CampaignStatus(
                id=str(campaign.get('campaign_id', '')),
                name=campaign.get('campaign_name', 'Unknown'),
                platform=campaign.get('platform', 'Unknown'),
                status=status,
                spend_today=round(spend_today, 2),
                daily_budget=round(budget, 2),
                pacing_percent=round(pacing, 0),
                cpa=round(campaign.get('cpa', 0), 2),
                conversions=campaign.get('conversions', 0),
                last_update=datetime.now().isoformat()
            ))
        
        # Generate alerts (check for anomalies)
        alerts = []
        for campaign in today_campaigns:
            cpc = campaign.get('cpc', 0)
            cpa = campaign.get('cpa', 0)
            
            # High CPC alert
            if cpc > 5.0:
                alerts.append(Alert(
                    id=f"alert-cpc-{campaign.get('campaign_id')}",
                    timestamp=datetime.now().isoformat(),
                    severity="warning",
                    message=f"CPC elevated at ${cpc:.2f}",
                    campaign=campaign.get('campaign_name'),
                    metric="CPC"
                ))
            
            # High CPA alert
            if cpa > 20.0:
                alerts.append(Alert(
                    id=f"alert-cpa-{campaign.get('campaign_id')}",
                    timestamp=datetime.now().isoformat(),
                    severity="critical",
                    message=f"CPA critically high at ${cpa:.2f}",
                    campaign=campaign.get('campaign_name'),
                    metric="CPA"
                ))
        
        return MetricsSnapshot(
            timestamp=datetime.now().isoformat(),
            metrics=metrics,
            campaigns=campaigns,
            alerts=alerts[:10]  # Top 10 alerts
        )
        
    except Exception as e:
        logger.error(f"Error fetching real-time snapshot: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch real-time data: {str(e)}"
        )


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket: {str(e)}")


manager = ConnectionManager()


@router.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time data streaming
    
    Sends updates every 2 seconds with:
    - Current metrics
    - Campaign statuses
    - New alerts
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # Fetch current snapshot
            # Note: WebSocket doesn't have user auth in the same way
            # In production, you'd want to authenticate via token in initial message
            
            query = """
            SELECT 
                id as campaign_id,
                name as campaign_name,
                platform,
                spend,
                conversions,
                cpc,
                cpa,
                ctr,
                budget
            FROM campaigns
            WHERE date = date('now')
            ORDER BY spend DESC
            LIMIT 10
            """
            
            with db_manager.get_session() as session:
                result = session.execute(text(query))
                campaigns = [dict(r) for r in result.mappings().all()]
            
            # Build update message
            total_spend = sum(c.get('spend', 0) for c in campaigns)
            total_conversions = sum(c.get('conversions', 0) for c in campaigns)
            
            update = {
                "type": "metrics_update",
                "timestamp": datetime.now().isoformat(),
                "metrics": {
                    "spend": {
                        "current": round(total_spend, 2),
                        "change_percent": round((total_spend * 0.05), 1)  # Simulated change
                    },
                    "conversions": {
                        "current": total_conversions,
                        "change_percent": round((total_conversions * 0.03), 1)
                    }
                },
                "campaign_count": len(campaigns)
            }
            
            # Send update
            await websocket.send_text(json.dumps(update))
            
            # Wait 2 seconds before next update
            await asyncio.sleep(2)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        manager.disconnect(websocket)
