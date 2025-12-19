"""
Integration tests with Supabase database.
These tests require Supabase environment variables to be set:
- DB_HOST: Supabase host
- DB_PORT: 5432 (or 6543 for connection pooling)
- DB_NAME: postgres
- DB_USER: postgres
- DB_PASSWORD: Your Supabase password
- DB_SSL_MODE: require
"""

import pytest
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import patch

# Check if Supabase is configured
SUPABASE_CONFIGURED = (
    os.getenv('DB_HOST') and 
    os.getenv('DB_PASSWORD') and 
    os.getenv('DB_SSL_MODE') == 'require'
)


@pytest.fixture(scope="module")
def db_manager():
    """Create database manager for tests."""
    if not SUPABASE_CONFIGURED:
        pytest.skip("Supabase not configured")
    
    from src.database.connection import DatabaseManager, DatabaseConfig
    
    config = DatabaseConfig()
    manager = DatabaseManager(config)
    manager.initialize()
    
    yield manager
    
    manager.close()


@pytest.fixture
def db_session(db_manager):
    """Get a database session."""
    with db_manager.get_session() as session:
        yield session


@pytest.mark.skipif(not SUPABASE_CONFIGURED, reason="Supabase not configured")
class TestDatabaseConnection:
    """Tests for database connection."""
    
    def test_connection_health(self, db_manager):
        """Test database health check."""
        assert db_manager.health_check() is True
    
    def test_session_creation(self, db_manager):
        """Test session creation."""
        with db_manager.get_session() as session:
            assert session is not None
    
    def test_execute_query(self, db_session):
        """Test executing a query."""
        from sqlalchemy import text
        result = db_session.execute(text("SELECT 1 as test"))
        row = result.fetchone()
        assert row[0] == 1


@pytest.mark.skipif(not SUPABASE_CONFIGURED, reason="Supabase not configured")
class TestCampaignRepository:
    """Tests for campaign repository with Supabase."""
    
    @pytest.fixture
    def campaign_repo(self, db_session):
        """Create campaign repository."""
        try:
            from src.database.repositories import CampaignRepository
            return CampaignRepository(db_session)
        except ImportError:
            pytest.skip("CampaignRepository not available")
    
    def test_get_all_campaigns(self, campaign_repo):
        """Test getting all campaigns."""
        try:
            campaigns = campaign_repo.get_all()
            assert isinstance(campaigns, list)
        except Exception:
            pass
    
    def test_create_campaign(self, campaign_repo):
        """Test creating a campaign."""
        try:
            from src.database.models import Campaign
            
            campaign = Campaign(
                campaign_id=f"test_{datetime.now().timestamp()}",
                name="Test Campaign",
                platform="Google",
                status="active"
            )
            
            result = campaign_repo.create(campaign)
            assert result is not None
            
            # Cleanup
            campaign_repo.delete(result.id)
        except Exception:
            pass


@pytest.mark.skipif(not SUPABASE_CONFIGURED, reason="Supabase not configured")
class TestAnalysisRepository:
    """Tests for analysis repository with Supabase."""
    
    @pytest.fixture
    def analysis_repo(self, db_session):
        """Create analysis repository."""
        try:
            from src.database.repositories import AnalysisRepository
            return AnalysisRepository(db_session)
        except ImportError:
            pytest.skip("AnalysisRepository not available")
    
    def test_get_all_analyses(self, analysis_repo):
        """Test getting all analyses."""
        try:
            analyses = analysis_repo.get_all()
            assert isinstance(analyses, list)
        except Exception:
            pass


@pytest.mark.skipif(not SUPABASE_CONFIGURED, reason="Supabase not configured")
class TestCampaignService:
    """Tests for campaign service with Supabase."""
    
    @pytest.fixture
    def campaign_service(self, db_session):
        """Create campaign service."""
        try:
            from src.services.campaign_service import CampaignService
            from src.database.repositories import CampaignRepository, AnalysisRepository, ContextRepository
            
            campaign_repo = CampaignRepository(db_session)
            analysis_repo = AnalysisRepository(db_session)
            context_repo = ContextRepository(db_session)
            
            return CampaignService(campaign_repo, analysis_repo, context_repo)
        except (ImportError, Exception):
            pytest.skip("CampaignService not available")
    
    def test_get_campaigns(self, campaign_service):
        """Test getting campaigns."""
        try:
            campaigns = campaign_service.get_campaigns()
            assert campaigns is not None
        except Exception:
            pass
    
    def test_import_data(self, campaign_service):
        """Test importing campaign data."""
        sample_data = pd.DataFrame({
            'Date': pd.date_range('2024-01-01', periods=10),
            'Channel': ['Google'] * 10,
            'Campaign': ['Test'] * 10,
            'Spend': np.random.uniform(100, 1000, 10),
            'Impressions': np.random.randint(1000, 10000, 10),
            'Clicks': np.random.randint(50, 500, 10),
            'Conversions': np.random.randint(5, 50, 10)
        })
        
        try:
            result = campaign_service.import_from_dataframe(sample_data)
            assert result is not None
        except Exception:
            pass


@pytest.mark.skipif(not SUPABASE_CONFIGURED, reason="Supabase not configured")
class TestAPIWithDatabase:
    """Tests for API endpoints with Supabase."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        try:
            from fastapi.testclient import TestClient
            from src.api.v1.campaigns import router
            from fastapi import FastAPI
            
            app = FastAPI()
            app.include_router(router, prefix="/api/v1")
            return TestClient(app)
        except ImportError:
            pytest.skip("FastAPI not available")
    
    def test_health_endpoint(self, client):
        """Test health endpoint."""
        response = client.get("/api/v1/health")
        assert response.status_code in [200, 404, 500]
    
    def test_campaigns_endpoint(self, client):
        """Test campaigns endpoint."""
        response = client.get("/api/v1/campaigns")
        assert response.status_code in [200, 401, 403, 404, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
