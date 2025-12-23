import os
# SET ENV VARS BEFORE IMPORTS
os.environ["RATE_LIMIT_ENABLED"] = "false"
os.environ["DATABASE_URL"] = "sqlite:///./test_pca.db"

from datetime import timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.api.main_v3 import app
from src.database.models import Base
from src.database.connection import get_db, get_db_manager
from src.api.middleware.auth import create_access_token
from src.services.user_service import UserService

# Use file-based SQLite for all integration tests to share data across connections
SQLITE_URL = "sqlite:///./test_pca.db"

import pytest

@pytest.fixture(scope="session")
def engine():
    engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return engine

@pytest.fixture(scope="function")
def db_session(engine):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function", autouse=True)
def override_get_db(db_session):
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def client():
    return TestClient(app)

@pytest.fixture(scope="function")
def test_user(db_session):
    """Create a standard free user."""
    service = UserService(db_session)
    # Ensure fresh start
    from src.database.user_models import User
    existing = db_session.query(User).filter(User.username == "testuser").first()
    if existing:
        return existing
        
    return service.create_user("testuser", "test@example.com", "Password123!", tier="free")

@pytest.fixture(scope="function")
def pro_user(db_session):
    """Create a pro user."""
    service = UserService(db_session)
    return service.create_user("prouser", "pro@example.com", "Password123!", tier="pro")

@pytest.fixture(scope="function")
def enterprise_user(db_session):
    """Create an enterprise user."""
    service = UserService(db_session)
    return service.create_user("entuser", "ent@example.com", "Password123!", tier="enterprise")

@pytest.fixture(scope="function")
def auth_headers(test_user):
    token = create_access_token(
        data={"sub": test_user.username, "role": test_user.role, "tier": test_user.tier},
        expires_delta=timedelta(hours=1)
    )
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="function")
def pro_auth_headers(pro_user):
    token = create_access_token(
        data={"sub": pro_user.username, "role": pro_user.role, "tier": pro_user.tier},
        expires_delta=timedelta(hours=1)
    )
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="function")
def ent_auth_headers(enterprise_user):
    token = create_access_token(
        data={"sub": enterprise_user.username, "role": enterprise_user.role, "tier": enterprise_user.tier},
        expires_delta=timedelta(hours=1)
    )
    return {"Authorization": f"Bearer {token}"}
