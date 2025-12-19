"""
Rate Limiting Middleware.

Implements request rate limiting to prevent abuse.
"""

import os
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

# Rate limit configuration
RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
RATE_LIMIT_DEFAULT = os.getenv("RATE_LIMIT_DEFAULT", "10/minute")

# Rate limit tiers
RATE_LIMITS = {
    "free": "10/minute",
    "pro": "100/minute",
    "enterprise": "1000/minute"
}


def get_rate_limit_key(request: Request) -> str:
    """
    Get rate limit key from request.
    
    Uses user ID if authenticated, otherwise IP address.
    
    Args:
        request: FastAPI request
        
    Returns:
        Rate limit key
    """
    # Try to get user from request state (set by auth middleware)
    user = getattr(request.state, "user", None)
    
    if user:
        return f"user:{user.get('username')}"
    
    # Fall back to IP address
    return get_remote_address(request)


def get_user_rate_limit(request: Request) -> str:
    """
    Get rate limit for user based on tier.
    
    Args:
        request: FastAPI request
        
    Returns:
        Rate limit string (e.g., "10/minute")
    """
    user = getattr(request.state, "user", None)
    
    if user:
        tier = user.get("tier", "free")
        return RATE_LIMITS.get(tier, RATE_LIMIT_DEFAULT)
    
    return RATE_LIMIT_DEFAULT


def setup_rate_limiter() -> Limiter:
    """
    Setup and configure rate limiter.
    
    Returns:
        Configured Limiter instance
    """
    limiter = Limiter(
        key_func=get_rate_limit_key,
        default_limits=[RATE_LIMIT_DEFAULT] if RATE_LIMIT_ENABLED else []
    )
    
    return limiter


# Create limiter instance
limiter = setup_rate_limiter()
