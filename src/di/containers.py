"""
Dependency Injection containers using dependency-injector.
Provides centralized configuration and dependency management.
"""

import os
from dependency_injector import containers, providers
from src.database.connection import DatabaseManager, DatabaseConfig
from src.database.repositories import (
    CampaignRepository,
    AnalysisRepository,
    QueryHistoryRepository,
    LLMUsageRepository,
    CampaignContextRepository
)


class DatabaseContainer(containers.DeclarativeContainer):
    """Container for database-related dependencies."""
    
    config = providers.Configuration()
    
    # Database configuration
    db_config = providers.Singleton(
        DatabaseConfig
    )
    
    # Database manager
    db_manager = providers.Singleton(
        DatabaseManager,
        config=db_config
    )
    
    # Session factory
    session_factory = providers.Factory(
        db_manager.provided.get_session_direct
    )


class RepositoryContainer(containers.DeclarativeContainer):
    """Container for repository dependencies."""
    
    db = providers.DependenciesContainer()
    
    # Repositories
    campaign_repository = providers.Factory(
        CampaignRepository,
        session=db.session_factory
    )
    
    analysis_repository = providers.Factory(
        AnalysisRepository,
        session=db.session_factory
    )
    
    query_history_repository = providers.Factory(
        QueryHistoryRepository,
        session=db.session_factory
    )
    
    llm_usage_repository = providers.Factory(
        LLMUsageRepository,
        session=db.session_factory
    )
    
    campaign_context_repository = providers.Factory(
        CampaignContextRepository,
        session=db.session_factory
    )


class ServiceContainer(containers.DeclarativeContainer):
    """Container for service-level dependencies."""
    
    config = providers.Configuration()
    repositories = providers.DependenciesContainer()
    
    # Analytics services
    from src.analytics.auto_insights import MediaAnalyticsExpert
    
    analytics_expert = providers.Factory(
        MediaAnalyticsExpert,
        use_anthropic=config.use_anthropic,
        anthropic_api_key=config.anthropic_api_key,
        openai_api_key=config.openai_api_key,
        gemini_api_key=config.gemini_api_key
    )


class ApplicationContainer(containers.DeclarativeContainer):
    """Main application container."""
    
    config = providers.Configuration()
    
    # Wire configuration from environment
    config.use_anthropic.from_env("USE_ANTHROPIC", default=False, as_=bool)
    config.anthropic_api_key.from_env("ANTHROPIC_API_KEY", default="")
    config.openai_api_key.from_env("OPENAI_API_KEY", default="")
    config.gemini_api_key.from_env("GEMINI_API_KEY", default="")
    
    # Database container
    database = providers.Container(
        DatabaseContainer
    )
    
    # Repository container
    repositories = providers.Container(
        RepositoryContainer,
        db=database
    )
    
    # Service container
    services = providers.Container(
        ServiceContainer,
        config=config,
        repositories=repositories
    )


# Global application container instance
app_container = ApplicationContainer()


def init_container():
    """Initialize the application container."""
    # Initialize database
    app_container.database.db_manager().initialize()
    return app_container


def get_container() -> ApplicationContainer:
    """Get the application container."""
    return app_container
