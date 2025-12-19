"""
API v1 Router.
"""

from fastapi import APIRouter

# Create v1 router
router_v1 = APIRouter(prefix="/api/v1", tags=["v1"])

# Import and include sub-routers
from .auth import router as auth_router
from .campaigns import router as campaigns_router
from .user_management import router as user_management_router
from .api_keys import router as api_keys_router
from .webhooks import router as webhooks_router

router_v1.include_router(auth_router)
router_v1.include_router(campaigns_router)
router_v1.include_router(user_management_router)
router_v1.include_router(api_keys_router)
router_v1.include_router(webhooks_router)

__all__ = ['router_v1']

