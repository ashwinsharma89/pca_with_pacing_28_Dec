"""
Pytest configuration and shared fixtures.

This file provides common fixtures and configuration for all tests.
"""

import os
import sys
from pathlib import Path
from typing import Generator, Dict, Any
from unittest.mock import Mock, MagicMock

import pytest
import pandas as pd
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()


# ============================================================================
# Pytest Configuration
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, no external dependencies)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (may use external services)"
    )
    config.addinivalue_line(
        "markers", "slow: Slow tests (may take several seconds)"
    )
    config.addinivalue_line(
        "markers", "llm: Tests that use LLM APIs (requires API keys)"
    )
    config.addinivalue_line(
        "markers", "db: Tests that use database"
    )


# ============================================================================
# Mock LLM Responses
# ============================================================================

@pytest.fixture
def mock_llm_response():
    """Mock LLM API response."""
    return {
        "choices": [
            {
                "message": {
                    "content": "This is a mock LLM response for testing.",
                    "role": "assistant"
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150
        }
    }


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Mock OpenAI response"
    mock_response.usage.prompt_tokens = 100
    mock_response.usage.completion_tokens = 50
    mock_response.usage.total_tokens = 150
    
    mock_client.chat.completions.create.return_value = mock_response
    
    return mock_client


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.content = [MagicMock()]
    mock_response.content[0].text = "Mock Anthropic response"
    mock_response.usage.input_tokens = 100
    mock_response.usage.output_tokens = 50
    
    mock_client.messages.create.return_value = mock_response
    
    return mock_client


# ============================================================================
# Sample Data Fixtures
# ============================================================================

@pytest.fixture
def sample_campaign_data() -> pd.DataFrame:
    """Sample campaign data for testing."""
    return pd.DataFrame({
        'Campaign_Name': ['Campaign A', 'Campaign B', 'Campaign C'],
        'Platform': ['Google', 'Facebook', 'Instagram'],
        'Date': pd.date_range('2024-01-01', periods=3),
        'Spend': [1000.0, 1500.0, 800.0],
        'Impressions': [50000, 75000, 40000],
        'Clicks': [2500, 3000, 1600],
        'Conversions': [100, 120, 64],
        'Revenue': [5000.0, 6000.0, 3200.0]
    })


@pytest.fixture
def sample_campaign_dict() -> Dict[str, Any]:
    """Sample campaign dictionary for testing."""
    return {
        'campaign_id': 'test-campaign-123',
        'name': 'Test Campaign',
        'objective': 'awareness',
        'status': 'active',
        'start_date': '2024-01-01',
        'end_date': '2024-12-31',
        'budget': 10000.0
    }


@pytest.fixture
def sample_analysis_result() -> Dict[str, Any]:
    """Sample analysis result for testing."""
    return {
        'executive_summary': {
            'overview': 'Campaign performed well',
            'highlights': [
                'CTR above industry average',
                'Strong conversion rate',
                'Positive ROI'
            ]
        },
        'metrics': {
            'total_spend': 3300.0,
            'total_clicks': 7100,
            'avg_ctr': 4.3,
            'avg_cpc': 0.46
        },
        'insights': [
            {
                'title': 'High CTR on Google',
                'description': 'Google campaigns show 5% CTR',
                'confidence': 95
            }
        ],
        'recommendations': [
            {
                'title': 'Increase Google budget',
                'description': 'Allocate more budget to high-performing platform',
                'priority': 'high',
                'expected_impact': '+20% conversions'
            }
        ]
    }


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture
def mock_db_session():
    """Mock database session."""
    session = MagicMock()
    session.query.return_value = session
    session.filter.return_value = session
    session.first.return_value = None
    session.all.return_value = []
    
    return session


@pytest.fixture
def temp_sqlite_db(tmp_path):
    """Temporary SQLite database for testing."""
    db_path = tmp_path / "test.db"
    return f"sqlite:///{db_path}"


# ============================================================================
# API Fixtures
# ============================================================================

@pytest.fixture
def mock_jwt_token() -> str:
    """Mock JWT token for testing."""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0X3VzZXIiLCJyb2xlIjoidXNlciIsInRpZXIiOiJmcmVlIn0.mock_signature"


@pytest.fixture
def mock_user() -> Dict[str, Any]:
    """Mock user for testing."""
    return {
        'username': 'test_user',
        'email': 'test@example.com',
        'role': 'user',
        'tier': 'free'
    }


@pytest.fixture
def mock_admin_user() -> Dict[str, Any]:
    """Mock admin user for testing."""
    return {
        'username': 'admin',
        'email': 'admin@example.com',
        'role': 'admin',
        'tier': 'enterprise'
    }


# ============================================================================
# File Fixtures
# ============================================================================

@pytest.fixture
def temp_csv_file(tmp_path, sample_campaign_data):
    """Temporary CSV file with sample data."""
    csv_path = tmp_path / "test_data.csv"
    sample_campaign_data.to_csv(csv_path, index=False)
    return csv_path


@pytest.fixture
def temp_directory(tmp_path):
    """Temporary directory for testing."""
    test_dir = tmp_path / "test_data"
    test_dir.mkdir()
    return test_dir


# ============================================================================
# Environment Fixtures
# ============================================================================

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables."""
    env_vars = {
        'OPENAI_API_KEY': 'test-openai-key',
        'ANTHROPIC_API_KEY': 'test-anthropic-key',
        'JWT_SECRET_KEY': 'test-secret-key',
        'RATE_LIMIT_ENABLED': 'false',
        'USE_SQLITE': 'true'
    }
    
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    
    return env_vars


# ============================================================================
# Cleanup
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Cleanup after each test."""
    yield
    # Add any cleanup logic here
    pass
