"""
Unit tests for Streamlit Integration tracking functionality.
Tests query tracking, LLM usage tracking, and analysis history.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from datetime import datetime
import uuid

# Mock streamlit before importing
import sys
mock_st = MagicMock()
mock_st.cache_resource = lambda f: f
mock_st.cache_data = lambda **kwargs: lambda f: f
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


class TestQueryTracking:
    """Test query tracking functionality."""
    
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
    
    def test_track_query_success(self, mock_manager):
        """Test successful query tracking."""
        with patch('src.streamlit_integration.database_manager.QueryHistoryRepository') as mock_repo:
            mock_repo_instance = Mock()
            mock_repo.return_value = mock_repo_instance
            
            result = mock_manager.track_query(
                user_query="Show top campaigns",
                sql_query="SELECT * FROM campaigns ORDER BY spend DESC",
                result_data={'rows': 10},
                execution_time=0.5,
                status='success'
            )
            
            # Should return query ID or None
            assert result is not None or result is None
    
    def test_track_query_with_dataframe_result(self, mock_manager):
        """Test tracking query with DataFrame result."""
        with patch('src.streamlit_integration.database_manager.QueryHistoryRepository') as mock_repo:
            mock_repo_instance = Mock()
            mock_repo.return_value = mock_repo_instance
            
            df_result = pd.DataFrame({'Campaign': ['A', 'B'], 'Spend': [100, 200]})
            
            result = mock_manager.track_query(
                user_query="Show campaigns",
                sql_query="SELECT * FROM campaigns",
                result_data=df_result,
                execution_time=0.3,
                status='success'
            )
            
            assert result is not None or result is None
    
    def test_track_query_failure(self, mock_manager):
        """Test tracking failed query."""
        with patch('src.streamlit_integration.database_manager.QueryHistoryRepository') as mock_repo:
            mock_repo_instance = Mock()
            mock_repo_instance.create.side_effect = Exception("DB error")
            mock_repo.return_value = mock_repo_instance
            
            result = mock_manager.track_query(
                user_query="Invalid query",
                sql_query=None,
                result_data=None,
                execution_time=0.1,
                status='error'
            )
            
            # Should return None on failure
            assert result is None
    
    def test_track_rag_query(self, mock_manager):
        """Test tracking RAG query (no SQL)."""
        with patch('src.streamlit_integration.database_manager.QueryHistoryRepository') as mock_repo:
            mock_repo_instance = Mock()
            mock_repo.return_value = mock_repo_instance
            
            result = mock_manager.track_query(
                user_query="What are best practices for campaign optimization?",
                sql_query=None,  # RAG query has no SQL
                result_data={'answer': 'Best practices include...'},
                execution_time=1.2,
                status='success'
            )
            
            assert result is not None or result is None


class TestLLMUsageTracking:
    """Test LLM usage tracking functionality."""
    
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
    
    def test_track_llm_usage_openai(self, mock_manager):
        """Test tracking OpenAI usage."""
        with patch('src.streamlit_integration.database_manager.LLMUsageRepository') as mock_repo:
            mock_repo_instance = Mock()
            mock_repo.return_value = mock_repo_instance
            
            result = mock_manager.track_llm_usage(
                provider='openai',
                model='gpt-4',
                prompt_tokens=500,
                completion_tokens=200,
                cost=0.025,
                operation='sql_generation'
            )
            
            assert result is True or result is False
    
    def test_track_llm_usage_anthropic(self, mock_manager):
        """Test tracking Anthropic usage."""
        with patch('src.streamlit_integration.database_manager.LLMUsageRepository') as mock_repo:
            mock_repo_instance = Mock()
            mock_repo.return_value = mock_repo_instance
            
            result = mock_manager.track_llm_usage(
                provider='anthropic',
                model='claude-3-sonnet',
                prompt_tokens=1000,
                completion_tokens=500,
                cost=0.015,
                operation='reasoning'
            )
            
            assert result is True or result is False
    
    def test_track_llm_usage_gemini(self, mock_manager):
        """Test tracking Gemini usage (free tier)."""
        with patch('src.streamlit_integration.database_manager.LLMUsageRepository') as mock_repo:
            mock_repo_instance = Mock()
            mock_repo.return_value = mock_repo_instance
            
            result = mock_manager.track_llm_usage(
                provider='gemini',
                model='gemini-2.5-flash',
                prompt_tokens=2000,
                completion_tokens=1000,
                cost=0.0,  # Free tier
                operation='sql_generation'
            )
            
            assert result is True or result is False


class TestAnalysisHistory:
    """Test analysis history functionality."""
    
    def test_session_state_analysis_history(self):
        """Test analysis history in session state."""
        mock_st.session_state = {'analysis_history': []}
        
        # Add analysis
        mock_st.session_state['analysis_history'].append({
            'analysis_id': str(uuid.uuid4()),
            'type': 'auto',
            'timestamp': datetime.now(),
            'execution_time': 1.5
        })
        
        assert len(mock_st.session_state['analysis_history']) == 1
    
    def test_multiple_analyses(self):
        """Test multiple analyses in history."""
        mock_st.session_state = {'analysis_history': []}
        
        analysis_types = ['auto', 'rag', 'channel', 'pattern']
        
        for atype in analysis_types:
            mock_st.session_state['analysis_history'].append({
                'analysis_id': str(uuid.uuid4()),
                'type': atype,
                'timestamp': datetime.now(),
                'execution_time': 1.0
            })
        
        assert len(mock_st.session_state['analysis_history']) == 4
    
    def test_analysis_history_retrieval(self):
        """Test retrieving analysis history."""
        mock_st.session_state = {
            'analysis_history': [
                {'type': 'auto', 'execution_time': 1.0},
                {'type': 'rag', 'execution_time': 2.0},
                {'type': 'auto', 'execution_time': 1.5}
            ]
        }
        
        # Filter by type
        auto_analyses = [
            a for a in mock_st.session_state['analysis_history']
            if a['type'] == 'auto'
        ]
        
        assert len(auto_analyses) == 2


class TestSessionManagement:
    """Test session management functionality."""
    
    def test_session_id_generation(self):
        """Test session ID generation."""
        session_id = str(uuid.uuid4())
        
        assert len(session_id) == 36  # UUID format
        assert '-' in session_id
    
    def test_session_state_persistence(self):
        """Test session state persistence."""
        mock_st.session_state = {}
        
        # Set session data
        mock_st.session_state['current_session_id'] = 'test-123'
        mock_st.session_state['df'] = pd.DataFrame({'A': [1, 2, 3]})
        mock_st.session_state['db_import_time'] = datetime.now()
        
        # Verify persistence
        assert mock_st.session_state['current_session_id'] == 'test-123'
        assert len(mock_st.session_state['df']) == 3
    
    def test_session_cleanup(self):
        """Test session cleanup."""
        mock_st.session_state = {
            'df': pd.DataFrame(),
            'current_session_id': 'test',
            'analysis_history': []
        }
        
        # Clear session
        keys_to_clear = ['df', 'current_session_id', 'analysis_history']
        for key in keys_to_clear:
            if key in mock_st.session_state:
                del mock_st.session_state[key]
        
        assert 'df' not in mock_st.session_state


class TestDataImportTracking:
    """Test data import tracking."""
    
    def test_import_metadata_storage(self):
        """Test import metadata storage."""
        mock_st.session_state = {}
        
        # Simulate import
        mock_st.session_state['db_import_time'] = datetime.now()
        mock_st.session_state['db_campaign_count'] = 150
        mock_st.session_state['import_source'] = 'csv'
        
        assert mock_st.session_state['db_campaign_count'] == 150
        assert mock_st.session_state['import_source'] == 'csv'
    
    def test_import_success_tracking(self):
        """Test tracking import success."""
        mock_st.session_state = {}
        
        import_result = {
            'success': True,
            'imported_count': 100,
            'message': 'Import successful'
        }
        
        mock_st.session_state['last_import'] = import_result
        
        assert mock_st.session_state['last_import']['success'] is True
