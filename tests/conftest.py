import subprocess
import time
import socket
import os
from contextlib import closing
import pytest
from dotenv import load_dotenv

# Load .env file to get DATABASE_URL (Supabase)
load_dotenv()

# Hybrid Test Configuration
# Priority: 1. DATABASE_URL from .env (Supabase) 2. Docker 3. Local fallback
DOCKER_COMPOSE_FILE = "docker-compose.test.yml"
LOCAL_FALLBACK_URL = "postgresql://ashwin@localhost:5433/test_pca"

# Get Supabase URL from environment (set in .env file)
SUPABASE_URL = os.environ.get("DATABASE_URL")

# Use Supabase if available, otherwise local fallback
if SUPABASE_URL and "supabase" in SUPABASE_URL.lower():
    DEFAULT_DB_URL = SUPABASE_URL
    print(f"[Config] Using Supabase database")
else:
    DEFAULT_DB_URL = LOCAL_FALLBACK_URL
    print(f"[Config] Using local fallback database")

# Set for app initialization
os.environ["DATABASE_URL"] = DEFAULT_DB_URL
os.environ["RATE_LIMIT_ENABLED"] = "false"
os.environ["USE_SQLITE"] = "false"

from datetime import timedelta
import io
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.api.main_v3 import app
from src.database.models import Base
from src.database.connection import get_db, get_db_manager
from src.api.middleware.auth import create_access_token
from src.services.user_service import UserService


def is_port_open(host, port):
    """Check if a port is open."""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(1)
        return sock.connect_ex((host, port)) == 0

def wait_for_postgres(url, retries=10, delay=1):
    """Wait for PostgreSQL to be ready."""
    from sqlalchemy import create_engine
    for i in range(retries):
        try:
            engine = create_engine(url)
            with engine.connect() as conn:
                return True
        except Exception:
            time.sleep(delay)
    return False

@pytest.fixture(scope="session")
def engine():
    """
    Hybrid Database Engine Fixture:
    Priority: 1. Supabase (cloud) 2. Docker container 3. Local fallback
    """
    db_url = DEFAULT_DB_URL  # Use Supabase from .env if available
    use_docker = False
    use_supabase = "supabase" in db_url.lower() if db_url else False
    
    if use_supabase:
        print(f"\n[DEBUG] ✅ Using Supabase database")
    # Try Docker only if not using Supabase
    elif os.environ.get("SKIP_DOCKER"):
        print("\n[DEBUG] SKIP_DOCKER set. Using local fallback.")
    else:
        try:
            print("\n[DEBUG] Attempting to start test containers...")
            subprocess.run(
                ["docker-compose", "-f", DOCKER_COMPOSE_FILE, "up", "-d", "postgres-test"],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                timeout=30
            )
            if wait_for_postgres("postgresql://pca_test:pca_test_password@localhost:5434/pca_test_db"):
                db_url = "postgresql://pca_test:pca_test_password@localhost:5434/pca_test_db"
                print("[DEBUG] ✅ Using Dockerized Test DB")
                use_docker = True
            else:
                print("[DEBUG] ⚠️ Docker DB started but unreachable. Using fallback.")
        except Exception as e:
            print(f"[DEBUG] ⚠️ Docker unavailable ({e}). Using current DB URL.")

    # Configure Environment
    os.environ["DATABASE_URL"] = db_url
    print(f"[DEBUG] Test Database URL: {db_url.split('@')[-1] if '@' in db_url else db_url}")
    
    engine = create_engine(db_url)
    
    # 3. Setup Schema
    from src.database.user_models import User, PasswordResetToken
    from src.database.models import QueryHistory, LLMUsage
    
    # Use safer cleanup
    print("[DEBUG] Resetting database schema...")
    try:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"[DEBUG] Schema reset warning: {e}")
        # Try just creating if drop fails (e.g. locks)
        Base.metadata.create_all(bind=engine)

    yield engine
    
    # 4. Cleanup
    engine.dispose()
    if use_docker:
        print("[DEBUG] Stopping test containers...")
        subprocess.run(
            ["docker-compose", "-f", DOCKER_COMPOSE_FILE, "down"],
            check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

@pytest.fixture(scope="function")
def db_session(engine):
    print("\n[DEBUG] db_session fixture started")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    # Clean up important tables before each test
    from src.database.user_models import User
    from src.database.models import QueryHistory, LLMUsage
    try:
        session.query(User).delete()
        session.query(QueryHistory).delete()
        session.query(LLMUsage).delete()
        session.commit()
        users = session.query(User).all()
        print(f"\n[DEBUG] Database cleaned. Users remaining: {[u.username for u in users]}")
    except Exception as e:
        print(f"\n[DEBUG] Cleanup failed: {e}")
        session.rollback()
        
    try:
        yield session
    finally:
        session.close()

@pytest.fixture(scope="function", autouse=True)
def override_get_db(db_session):
    def _override_get_db():
        try:
            # Final check before test starts
            from src.database.user_models import User
            users = db_session.query(User).all()
            print(f"[DEBUG] Inside override_get_db. Users: {[u.username for u in users]}")
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
def test_user_data():
    """Registration data for the standard test user."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Password123!",
        "tier": "free"
    }

@pytest.fixture(scope="function")
def test_user(db_session, test_user_data):
    """Create a standard free user."""
    service = UserService(db_session)
    data = test_user_data.copy()
    tier = data.pop("tier", "free")
    return service.create_user(**data, tier=tier)

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

@pytest.fixture(autouse=True)
def mock_analytics_services():
    """Mock out all LLM-based analytics services to prevent API calls."""
    with patch("src.analytics.auto_insights.MediaAnalyticsExpert") as MockExpert, \
         patch("src.api.v1.campaigns.MediaAnalyticsExpert") as MockExpertAPI, \
         patch("src.api.v1.campaigns.query_engine") as MockQueryEngineAPI, \
         patch("src.api.v1.intelligence.NaturalLanguageQueryEngine") as MockIntelligenceQueryEngine, \
         patch("src.query_engine.nl_to_sql.NaturalLanguageQueryEngine") as MockQueryEngine, \
         patch("src.agents.reasoning_agent.ReasoningAgent") as MockReasoningAgent, \
         patch("src.agents.enhanced_reasoning_agent.EnhancedReasoningAgent") as MockEnhancedReasoningAgent:
        
        # Configure MediaAnalyticsExpert mock
        expert_instance = MockExpert.return_value
        expert_instance.generate_executive_summary.return_value = {
            "summary": "Mocked summary",
            "insights": [],
            "recommendations": []
        }
        expert_instance.analyze_campaigns.return_value = "Mocked analysis"
        # FIX: Return dict for calculate_metrics to avoid serialization error
        expert_instance.calculate_metrics.return_value = {
            "ctr": 1.5,
            "cpc": 2.0,
            "cpa": 10.0,
            "roas": 5.0,
            "spend": 1000.0,
            "impressions": 10000,
            "clicks": 500,
            "conversions": 50
        }
        
        # Configure NL Query Engine mock
        query_instance = MockQueryEngine.return_value
        # FIX: Mock ask() which is used by chat_global
        query_instance.ask.return_value = {
            "success": True,
            "answer": "Mocked Answer from NL Query",
            "sql": "SELECT 1",
            "data": []
        }
        query_instance.process_query.return_value = {
            "sql": "SELECT * FROM campaigns",
            "explanation": "Mocked SQL",
            "results": []
        }
        # FIX: Mock load_parquet_data to prevent crash if instance is real
        query_instance.load_parquet_data.return_value = None
        
        yield {
            "expert": MockExpert,
            "query_engine": MockQueryEngine,
            "reasoning": MockReasoningAgent,
            "enhanced_reasoning": MockEnhancedReasoningAgent
        }

@pytest.fixture(scope="function")
def auth_token(test_user):
    """Create auth token without Bearer prefix for tests that need just the token."""
    token = create_access_token(
        data={"sub": test_user.username, "role": test_user.role, "tier": test_user.tier},
        expires_delta=timedelta(hours=1)
    )
    return token

@pytest.fixture(scope="function")
def sample_csv_file():
    """Create sample campaign CSV data for testing."""
    df = pd.DataFrame({
        'Date': ['2024-01-01', '2024-01-02'],
        'Platform': ['Google Ads', 'Meta Ads'],
        'Campaign_Name': ['C1', 'C2'],
        'Spend_USD': [100.0, 200.0],
        'Impressions': [1000, 2000],
        'Clicks': [10, 20],
        'Conversions': [1, 2],
        'Revenue_USD': [500.0, 1000.0]
    })
    csv_buffer = io.BytesIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    return csv_buffer

@pytest.fixture(scope="function")
def sample_excel_file():
    """Create sample campaign Excel data for testing."""
    df = pd.DataFrame({
        'Date': ['2024-01-01', '2024-01-02'],
        'Platform': ['Google Ads', 'Meta Ads'],
        'Campaign_Name': ['C1', 'C2'],
        'Spend_USD': [100.0, 200.0],
        'Impressions': [1000, 2000],
        'Clicks': [10, 20],
        'Conversions': [1, 2],
        'Revenue_USD': [500.0, 1000.0]
    })
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    excel_buffer.seek(0)
    return excel_buffer


# Import agent fixtures for pattern detection tests
try:
    from tests.fixtures.agent_fixtures import (
        sample_campaign_data,
        campaign_data_with_creative_fatigue,
        campaign_data_with_audience_saturation,
        campaign_data_with_trend,
        campaign_data_with_anomalies,
        multi_campaign_data,
        mock_llm_client,
        mock_rag_retriever,
        mock_benchmark_engine,
        sample_patterns,
        campaign_context
    )
except ImportError as e:
    print(f"Warning: Could not import agent fixtures: {e}")


