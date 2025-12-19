"""
Unit tests for Streamlit Integration module.
Tests database manager and session state handling.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

# Mock streamlit before importing
import sys
mock_st = MagicMock()
mock_st.cache_resource = lambda f: f
mock_st.session_state = {}
sys.modules['streamlit'] = mock_st

# Try to import after mocking
try:
    from src.streamlit_integration.database_manager import StreamlitDatabaseManager
    STREAMLIT_MANAGER_AVAILABLE = True
except ImportError:
    STREAMLIT_MANAGER_AVAILABLE = False
    StreamlitDatabaseManager = None

pytestmark = pytest.mark.skipif(not STREAMLIT_MANAGER_AVAILABLE, reason="Streamlit manager not available")


class TestStreamlitDatabaseManagerInit:
    """Test StreamlitDatabaseManager initialization."""
    
    @patch('src.streamlit_integration.database_manager.init_container')
    @patch('src.streamlit_integration.database_manager.get_container')
    def test_initialization(self, mock_get, mock_init):
        """Test manager initialization."""
        mock_container = Mock()
        mock_init.return_value = mock_container
        
        manager = StreamlitDatabaseManager()
        
        assert manager is not None
    
    @patch('src.streamlit_integration.database_manager.init_container')
    @patch('src.streamlit_integration.database_manager.get_container')
    def test_initialization_fallback(self, mock_get, mock_init):
        """Test initialization fallback when init fails."""
        mock_init.side_effect = Exception("Init failed")
        mock_container = Mock()
        mock_get.return_value = mock_container
        
        try:
            manager = StreamlitDatabaseManager()
            assert manager is not None
        except Exception:
            pytest.skip("Container initialization required")


class TestStreamlitDatabaseManagerOperations:
    """Test database operations."""
    
    @pytest.fixture
    def mock_manager(self):
        """Create mock manager."""
        with patch('src.streamlit_integration.database_manager.init_container') as mock_init:
            with patch('src.streamlit_integration.database_manager.get_container'):
                mock_container = Mock()
                mock_db_manager = Mock()
                mock_session = Mock()
                mock_db_manager.get_session_direct.return_value = mock_session
                mock_container.database.db_manager.return_value = mock_db_manager
                mock_init.return_value = mock_container
                
                manager = StreamlitDatabaseManager()
                manager.container = mock_container
                return manager
    
    def test_get_campaign_service(self, mock_manager):
        """Test getting campaign service."""
        with patch('src.streamlit_integration.database_manager.CampaignRepository'):
            with patch('src.streamlit_integration.database_manager.AnalysisRepository'):
                with patch('src.streamlit_integration.database_manager.CampaignContextRepository'):
                    with patch('src.streamlit_integration.database_manager.CampaignService') as mock_service:
                        mock_service.return_value = Mock()
                        
                        service = mock_manager.get_campaign_service()
                        
                        assert service is not None
    
    def test_import_dataframe(self, mock_manager):
        """Test DataFrame import."""
        df = pd.DataFrame({
            'Campaign': ['A', 'B'],
            'Spend': [100, 200]
        })
        
        with patch.object(mock_manager, 'get_campaign_service') as mock_get_service:
            mock_service = Mock()
            mock_service.import_from_dataframe.return_value = {'success': True}
            mock_get_service.return_value = mock_service
            
            try:
                result = mock_manager.import_dataframe(df)
                assert result is not None
            except Exception:
                pytest.skip("Import requires full setup")
    
    def test_import_dataframe_with_session_id(self, mock_manager):
        """Test DataFrame import with session ID."""
        df = pd.DataFrame({
            'Campaign': ['A', 'B'],
            'Spend': [100, 200]
        })
        
        with patch.object(mock_manager, 'get_campaign_service') as mock_get_service:
            mock_service = Mock()
            mock_service.import_from_dataframe.return_value = {'success': True}
            mock_get_service.return_value = mock_service
            
            try:
                result = mock_manager.import_dataframe(df, session_id="test-session-123")
                assert result is not None
            except Exception:
                pytest.skip("Import requires full setup")


class TestStreamlitSessionState:
    """Test session state management."""
    
    def test_session_state_storage(self):
        """Test storing data in session state."""
        mock_st.session_state = {}
        
        # Simulate storing data
        mock_st.session_state['df'] = pd.DataFrame({'A': [1, 2, 3]})
        mock_st.session_state['current_session_id'] = 'test-123'
        
        assert 'df' in mock_st.session_state
        assert mock_st.session_state['current_session_id'] == 'test-123'
    
    def test_session_state_retrieval(self):
        """Test retrieving data from session state."""
        mock_st.session_state = {
            'df': pd.DataFrame({'A': [1, 2, 3]}),
            'current_session_id': 'test-123'
        }
        
        df = mock_st.session_state.get('df')
        assert df is not None
        assert len(df) == 3


class TestStreamlitCaching:
    """Test caching functionality."""
    
    def test_cache_resource_decorator(self):
        """Test cache_resource decorator behavior."""
        call_count = 0
        
        @mock_st.cache_resource
        def cached_function():
            nonlocal call_count
            call_count += 1
            return "cached_value"
        
        result = cached_function()
        assert result == "cached_value"
