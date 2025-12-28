"""
API v1 Router.
"""

from fastapi import APIRouter
from loguru import logger

# Create v1 router
router_v1 = APIRouter(prefix="/api/v1", tags=["v1"])

# Import and include sub-routers
from .auth import router as auth_router
from .campaigns import router as campaigns_router
from .user_management import router as user_management_router
from .api_keys import router as api_keys_router
from .webhooks import router as webhooks_router
from .intelligence import router as intelligence_router
from .anomaly import router as anomaly_router
from .realtime import router as realtime_router
from .dashboards import router as dashboards_router
from .comparison import router as comparison_router
from .visualizations import router as visualizations_router
from .pacing_reports import router as pacing_reports_router

router_v1.include_router(auth_router)
router_v1.include_router(campaigns_router)
router_v1.include_router(user_management_router)
router_v1.include_router(api_keys_router)
router_v1.include_router(webhooks_router)
router_v1.include_router(intelligence_router)
router_v1.include_router(anomaly_router)
router_v1.include_router(realtime_router)
router_v1.include_router(dashboards_router)
router_v1.include_router(comparison_router)
router_v1.include_router(visualizations_router)
router_v1.include_router(pacing_reports_router)

__all__ = ['router_v1']

