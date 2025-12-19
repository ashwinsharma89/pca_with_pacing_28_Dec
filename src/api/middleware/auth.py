"""
JWT Authentication Middleware.

Provides JWT token generation, verification, and user authentication.
"""

import os
import sys
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from fastapi import HTTPException, Security, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import bcrypt
from loguru import logger

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))

# Security validation on import
if not SECRET_KEY:
    logger.error("🔴 CRITICAL: JWT_SECRET_KEY environment variable not set!")
    logger.error("Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(32))\"")
    sys.exit(1)

if SECRET_KEY in ["change-this-secret-key", "your-secure-random-secret-here-change-this"]:
    logger.error("🔴 CRITICAL: Using default/insecure JWT_SECRET_KEY!")
    logger.error("This is a SECURITY VULNERABILITY. Generate a secure secret immediately.")
    if os.getenv("PRODUCTION_MODE", "false").lower() == "true":
        logger.error("Refusing to start in production mode with insecure secret.")
        sys.exit(1)
    else:
        logger.warning("⚠️  Allowing insecure secret in development mode only.")
        logger.warning("⚠️  DO NOT deploy to production with this configuration!")

# Security scheme
security = HTTPBearer()

# NOTE: User authentication now uses database
# See src/services/user_service.py for user management
# See src/api/v1/user_management.py for user endpoints
# Use scripts/init_users.py to create initial admin user


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Bcrypt hashed password
        
    Returns:
        True if password matches
    """
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def get_user(username: str, db=None) -> Optional[Dict[str, Any]]:
    """
    Get user from database.
    
    Args:
        username: Username
        db: Database session (optional, for backward compatibility)
        
    Returns:
        User dict or None
        
    Note:
        This function is kept for backward compatibility.
        For new code, use UserService from src/services/user_service.py
    """
    if db is None:
        # Fallback: Try to get database session
        try:
            from src.database.connection import get_db_manager
            db_manager = get_db_manager()
            db = db_manager.get_session_direct()
        except Exception:
            logger.warning("Could not get database session for user lookup")
            return None
    
    try:
        from src.services.user_service import UserService
        user_service = UserService(db)
        user_model = user_service.get_user_by_username(username)
        
        # If not found by username, try by email
        if not user_model:
            user_model = user_service.get_user_by_email(username)
        
        if not user_model:
            return None
        
        # Convert to dict format for compatibility
        return {
            "username": user_model.username,
            "email": user_model.email,
            "hashed_password": user_model.hashed_password,
            "role": user_model.role,
            "tier": user_model.tier or "free"
        }
    except Exception as e:
        logger.error(f"Error getting user from database: {e}")
        return None
    finally:
        if db:
            try:
                db.close()
            except:
                pass


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate user with username and password.
    
    Args:
        username: Username
        password: Password
        
    Returns:
        User dict if authenticated, None otherwise
    """
    logger.info(f"Authenticating user: {username}")
    
    user = get_user(username)
    if not user:
        logger.warning(f"User not found in DB: {username}")
        return None
    
    logger.info(f"User found: {username}, Role: {user.get('role')}")
    
    is_valid = verify_password(password, user["hashed_password"])
    if not is_valid:
        logger.warning(f"Password mismatch for user: {username}")
        return None
    
    logger.info(f"Password verified for user: {username}")
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.
    
    Args:
        data: Data to encode in token
        expires_delta: Optional expiration time delta
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    logger.info(f"Created access token for user: {data.get('sub')}")
    
    return encoded_jwt


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> Dict[str, Any]:
    """
    Verify JWT token and return payload.
    
    Args:
        credentials: HTTP Bearer credentials
        
    Returns:
        Token payload
        
    Raises:
        HTTPException: If token is invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        return payload
        
    except JWTError as e:
        logger.error(f"JWT verification failed: {e}")
        raise credentials_exception


async def get_current_user(
    payload: Dict[str, Any] = Depends(verify_token)
) -> Dict[str, Any]:
    """
    Get current authenticated user.
    
    Args:
        payload: JWT token payload
        
    Returns:
        User dict
        
    Raises:
        HTTPException: If user not found
    """
    username = payload.get("sub")
    user = get_user(username)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


async def get_current_active_admin(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get current user and verify admin role.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User dict
        
    Raises:
        HTTPException: If user is not admin
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return current_user


def create_user(username: str, email: str, password: str, role: str = "user", tier: str = "free", db=None) -> Dict[str, Any]:
    """
    Create a new user in database.
    
    Args:
        username: Username
        email: Email
        password: Plain password
        role: User role
        tier: User tier
        db: Database session (optional)
        
    Returns:
        Created user dict
        
    Note:
        This function is kept for backward compatibility.
        For new code, use UserService from src/services/user_service.py
        Or use scripts/init_users.py to create users
    """
    if db is None:
        try:
            from src.database.connection import get_db_manager
            db_manager = get_db_manager()
            db = db_manager.get_session_direct()
        except Exception as e:
            logger.error(f"Could not get database session: {e}")
            raise HTTPException(
                status_code=500,
                detail="Database connection failed"
            )
    
    try:
        from src.services.user_service import UserService
        user_service = UserService(db)
        
        user_model = user_service.create_user(
            username=username,
            email=email,
            password=password,
            role=role,
            tier=tier
        )
        
        logger.info(f"Created user: {username}")
        
        return {
            "username": user_model.username,
            "email": user_model.email,
            "hashed_password": user_model.hashed_password,
            "role": user_model.role,
            "tier": user_model.tier or "free"
        }
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create user: {str(e)}"
        )
    finally:
        if db:
            try:
                db.close()
            except:
                pass
