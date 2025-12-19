"""
Streamlit-specific database manager.
Handles database operations with Streamlit caching and session state.
"""

import streamlit as st
import pandas as pd
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

from src.di import init_container, get_container
from src.services import CampaignService
from src.database.repositories import (
    CampaignRepository,
    AnalysisRepository,
    CampaignContextRepository,
    QueryHistoryRepository,
    LLMUsageRepository
)

logger = logging.getLogger(__name__)


class StreamlitDatabaseManager:
    """
    Manages database operations for Streamlit app.
    Integrates with Streamlit session state and caching.
    """
    
    def __init__(self):
        self.container = self._get_container()
    
    @staticmethod
    @st.cache_resource
    def _get_container():
        """Initialize and cache the DI container."""
        try:
            container = init_container()
            logger.info("✅ Database container initialized")
            return container
        except Exception as e:
            logger.error(f"❌ Failed to initialize container: {e}")
            # Fallback to get_container if init fails
            return get_container()
    
    def get_campaign_service(self) -> CampaignService:
        """Get campaign service with fresh session."""
        session = self.container.database.db_manager().get_session_direct()
        
        return CampaignService(
            campaign_repo=CampaignRepository(session),
            analysis_repo=AnalysisRepository(session),
            context_repo=CampaignContextRepository(session)
        )
    
    def import_dataframe(self, df: pd.DataFrame, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Import DataFrame to database and store in session state.
        
        Args:
            df: DataFrame to import
            session_id: Optional session ID for tracking
            
        Returns:
            Result dictionary with success status and message
        """
        try:
            # Generate session ID if not provided
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # Store in session state
            st.session_state.df = df
            st.session_state.current_session_id = session_id
            
            # Import to database
            campaign_service = self.get_campaign_service()
            result = campaign_service.import_from_dataframe(df)
            
            if result['success']:
                # Store import metadata
                st.session_state.db_import_time = datetime.now()
                st.session_state.db_campaign_count = result['imported_count']
                
                logger.info(f"✅ Imported {result['imported_count']} campaigns to database")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to import DataFrame: {e}")
            return {
                'success': False,
                'imported_count': 0,
                'message': f'Import failed: {str(e)}'
            }
    
    def get_campaigns(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 1000,
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Get campaigns from database as DataFrame.
        
        Args:
            filters: Optional filters
            limit: Maximum number of campaigns
            use_cache: Whether to use Streamlit cache
            
        Returns:
            DataFrame with campaigns
        """
        try:
            if use_cache:
                # Use cached version
                return self._get_campaigns_cached(
                    str(filters) if filters else "all",
                    limit
                )
            else:
                # Direct query
                campaign_service = self.get_campaign_service()
                campaigns = campaign_service.get_campaigns(filters=filters, limit=limit)
                return pd.DataFrame(campaigns) if campaigns else pd.DataFrame()
                
        except Exception as e:
            logger.error(f"❌ Failed to get campaigns: {e}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def _get_campaigns_cached(_self, filter_key: str, limit: int) -> pd.DataFrame:
        """Cached version of get_campaigns."""
        try:
            campaign_service = _self.get_campaign_service()
            
            # Parse filters from key safely
            filters = None
            if filter_key != "all":
                # Use ast.literal_eval for safe parsing (only allows literals)
                import ast
                try:
                    filters = ast.literal_eval(filter_key)
                except (ValueError, SyntaxError):
                    logger.warning(f"Invalid filter key format: {filter_key}")
                    filters = None
            
            campaigns = campaign_service.get_campaigns(filters=filters, limit=limit)
            return pd.DataFrame(campaigns) if campaigns else pd.DataFrame()
            
        except Exception as e:
            logger.error(f"❌ Cached query failed: {e}")
            return pd.DataFrame()
    
    def save_analysis(
        self,
        analysis_type: str,
        results: Dict[str, Any],
        execution_time: float
    ) -> Optional[str]:
        """
        Save analysis results to database.
        
        Args:
            analysis_type: Type of analysis ('auto', 'rag', 'channel', 'pattern')
            results: Analysis results
            execution_time: Execution time in seconds
            
        Returns:
            Analysis ID if successful
        """
        try:
            # Get session ID
            session_id = st.session_state.get('current_session_id')
            if not session_id:
                logger.warning("No session ID found, generating new one")
                session_id = str(uuid.uuid4())
                st.session_state.current_session_id = session_id
            
            # Save to database
            campaign_service = self.get_campaign_service()
            analysis_id = campaign_service.save_analysis(
                campaign_id=session_id,
                analysis_type=analysis_type,
                results=results,
                execution_time=execution_time
            )
            
            if analysis_id:
                # Store in session state
                if 'analysis_history' not in st.session_state:
                    st.session_state.analysis_history = []
                
                st.session_state.analysis_history.append({
                    'analysis_id': analysis_id,
                    'type': analysis_type,
                    'timestamp': datetime.now(),
                    'execution_time': execution_time
                })
                
                logger.info(f"✅ Saved analysis {analysis_id}")
            
            return analysis_id
            
        except Exception as e:
            logger.error(f"❌ Failed to save analysis: {e}")
            return None
    
    def track_query(
        self,
        user_query: str,
        sql_query: Optional[str],
        result_data: Any,
        execution_time: float,
        status: str = 'success'
    ) -> Optional[str]:
        """
        Track Q&A query in database.
        
        Args:
            user_query: User's natural language query
            sql_query: Generated SQL query
            result_data: Query results
            execution_time: Execution time in seconds
            status: Query status
            
        Returns:
            Query ID if successful
        """
        try:
            session = self.container.database.db_manager().get_session_direct()
            query_repo = QueryHistoryRepository(session)
            
            query_id = str(uuid.uuid4())
            
            query_repo.create({
                'query_id': query_id,
                'user_query': user_query,
                'sql_query': sql_query,
                'query_type': 'sql' if sql_query else 'rag',
                'result_data': result_data if isinstance(result_data, dict) else {'result': str(result_data)},
                'execution_time': execution_time,
                'status': status
            })
            
            query_repo.commit()
            session.close()
            
            logger.info(f"✅ Tracked query {query_id}")
            return query_id
            
        except Exception as e:
            logger.error(f"❌ Failed to track query: {e}")
            return None
    
    def track_llm_usage(
        self,
        provider: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        cost: float,
        operation: str
    ) -> bool:
        """
        Track LLM API usage.
        
        Args:
            provider: LLM provider ('openai', 'anthropic', 'gemini')
            model: Model name
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            cost: Cost in USD
            operation: Operation type
            
        Returns:
            True if successful
        """
        try:
            session = self.container.database.db_manager().get_session_direct()
            llm_repo = LLMUsageRepository(session)
            
            llm_repo.create({
                'provider': provider,
                'model': model,
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'total_tokens': prompt_tokens + completion_tokens,
                'cost': cost,
                'operation': operation,
                'request_id': st.session_state.get('current_session_id', 'unknown')
            })
            
            llm_repo.commit()
            session.close()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to track LLM usage: {e}")
            return False
    
    def get_llm_usage_stats(self, days: int = 30) -> Dict[str, Any]:
        """
        Get LLM usage statistics.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Usage statistics dictionary
        """
        try:
            from datetime import timedelta
            
            session = self.container.database.db_manager().get_session_direct()
            llm_repo = LLMUsageRepository(session)
            
            start_date = datetime.now() - timedelta(days=days)
            
            total_usage = llm_repo.get_total_usage(start_date=start_date)
            
            # Get usage by provider
            providers = ['openai', 'anthropic', 'gemini']
            provider_usage = {}
            
            for provider in providers:
                usage = llm_repo.get_usage_by_provider(provider, start_date=start_date)
                if usage['request_count'] > 0:
                    provider_usage[provider] = usage
            
            session.close()
            
            return {
                'total': total_usage,
                'by_provider': provider_usage,
                'period_days': days
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get LLM usage stats: {e}")
            return {'total': {}, 'by_provider': {}, 'period_days': days}
    
    def health_check(self) -> bool:
        """Check database health."""
        try:
            db_manager = self.container.database.db_manager()
            return db_manager.health_check()
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return False
    
    def get_aggregated_metrics(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get aggregated campaign metrics."""
        try:
            campaign_service = self.get_campaign_service()
            return campaign_service.get_aggregated_metrics(filters=filters)
        except Exception as e:
            logger.error(f"❌ Failed to get aggregated metrics: {e}")
            return {}


# Global instance
_db_manager: Optional[StreamlitDatabaseManager] = None


def get_streamlit_db_manager() -> StreamlitDatabaseManager:
    """Get or create global Streamlit database manager."""
    global _db_manager
    if _db_manager is None:
        _db_manager = StreamlitDatabaseManager()
    return _db_manager
