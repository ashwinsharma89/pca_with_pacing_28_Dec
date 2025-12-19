"""
Example: How to integrate PostgreSQL + DI with Streamlit app.

This shows how to replace in-memory storage with PostgreSQL.
"""

import streamlit as st
import pandas as pd
from src.di import init_container, get_container
from src.services import CampaignService

# Initialize dependency injection container (do this once at app startup)
@st.cache_resource
def initialize_app():
    """Initialize application container."""
    container = init_container()
    return container

# Get container
container = initialize_app()

# Example 1: Import campaigns from uploaded CSV
def import_campaigns_example():
    """Example of importing campaigns."""
    st.header("Import Campaigns")
    
    uploaded_file = st.file_uploader("Upload Campaign Data", type=['csv'])
    
    if uploaded_file and st.button("Import"):
        # Read CSV
        df = pd.read_csv(uploaded_file)
        
        # Get campaign service from container
        with container.database.db_manager().get_session() as session:
            from src.database.repositories import (
                CampaignRepository,
                AnalysisRepository,
                CampaignContextRepository
            )
            
            campaign_service = CampaignService(
                campaign_repo=CampaignRepository(session),
                analysis_repo=AnalysisRepository(session),
                context_repo=CampaignContextRepository(session)
            )
            
            # Import campaigns
            with st.spinner("Importing campaigns..."):
                result = campaign_service.import_from_dataframe(df)
            
            if result['success']:
                st.success(f"✅ {result['message']}")
            else:
                st.error(f"❌ {result['message']}")

# Example 2: Query campaigns with filters
def query_campaigns_example():
    """Example of querying campaigns."""
    st.header("Query Campaigns")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        platform = st.selectbox("Platform", ["All", "Google", "Facebook", "LinkedIn"])
    with col2:
        limit = st.number_input("Limit", min_value=10, max_value=1000, value=100)
    
    if st.button("Search"):
        # Get campaign service
        with container.database.db_manager().get_session() as session:
            from src.database.repositories import (
                CampaignRepository,
                AnalysisRepository,
                CampaignContextRepository
            )
            
            campaign_service = CampaignService(
                campaign_repo=CampaignRepository(session),
                analysis_repo=AnalysisRepository(session),
                context_repo=CampaignContextRepository(session)
            )
            
            # Build filters
            filters = {}
            if platform != "All":
                filters['platform'] = platform
            
            # Query campaigns
            campaigns = campaign_service.get_campaigns(filters=filters, limit=limit)
            
            # Display results
            if campaigns:
                st.success(f"Found {len(campaigns)} campaigns")
                
                # Convert to DataFrame for display
                df = pd.DataFrame(campaigns)
                st.dataframe(df)
                
                # Show aggregated metrics
                metrics = campaign_service.get_aggregated_metrics(filters=filters)
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Spend", f"${metrics['total_spend']:,.0f}")
                col2.metric("Total Clicks", f"{metrics['total_clicks']:,}")
                col3.metric("Total Conversions", f"{metrics['total_conversions']:,}")
                col4.metric("Avg CTR", f"{metrics['avg_ctr']:.2f}%")
            else:
                st.info("No campaigns found")

# Example 3: Save analysis results
def save_analysis_example():
    """Example of saving analysis results."""
    st.header("Save Analysis")
    
    campaign_id = st.text_input("Campaign ID")
    
    if st.button("Run & Save Analysis"):
        # Get analytics expert from container
        analytics_expert = container.services.analytics_expert()
        
        # Get campaign data (simplified example)
        with container.database.db_manager().get_session() as session:
            from src.database.repositories import CampaignRepository
            
            campaign_repo = CampaignRepository(session)
            campaign = campaign_repo.get_by_campaign_id(campaign_id)
            
            if not campaign:
                st.error(f"Campaign {campaign_id} not found")
                return
            
            # Run analysis (example - you'd use actual campaign data)
            import time
            start_time = time.time()
            
            with st.spinner("Running analysis..."):
                # Placeholder for actual analysis
                analysis_results = {
                    'insights': [
                        {'title': 'High CTR', 'description': 'CTR is above benchmark'},
                        {'title': 'Low CPA', 'description': 'Cost per acquisition is efficient'}
                    ],
                    'recommendations': [
                        {'priority': 'high', 'recommendation': 'Increase budget by 20%'},
                        {'priority': 'medium', 'recommendation': 'Test new ad creative'}
                    ],
                    'metrics': {
                        'total_spend': campaign.spend,
                        'total_conversions': campaign.conversions,
                        'avg_ctr': campaign.ctr
                    },
                    'executive_summary': {
                        'brief': 'Campaign performing well',
                        'detailed': 'Detailed analysis shows strong performance...'
                    }
                }
            
            execution_time = time.time() - start_time
            
            # Save analysis
            from src.database.repositories import (
                CampaignRepository,
                AnalysisRepository,
                CampaignContextRepository
            )
            
            campaign_service = CampaignService(
                campaign_repo=CampaignRepository(session),
                analysis_repo=AnalysisRepository(session),
                context_repo=CampaignContextRepository(session)
            )
            
            analysis_id = campaign_service.save_analysis(
                campaign_id=campaign_id,
                analysis_type='auto',
                results=analysis_results,
                execution_time=execution_time
            )
            
            if analysis_id:
                st.success(f"✅ Analysis saved! ID: {analysis_id}")
                st.json(analysis_results)
            else:
                st.error("Failed to save analysis")

# Example 4: View LLM usage
def view_llm_usage_example():
    """Example of viewing LLM usage."""
    st.header("LLM Usage Statistics")
    
    with container.database.db_manager().get_session() as session:
        from src.database.repositories import LLMUsageRepository
        
        llm_repo = LLMUsageRepository(session)
        
        # Get total usage
        total_usage = llm_repo.get_total_usage()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Tokens", f"{total_usage['total_tokens']:,}")
        col2.metric("Total Cost", f"${total_usage['total_cost']:.2f}")
        col3.metric("Total Requests", f"{total_usage['request_count']:,}")
        
        # Get usage by provider
        st.subheader("Usage by Provider")
        
        for provider in ['openai', 'anthropic', 'gemini']:
            provider_usage = llm_repo.get_usage_by_provider(provider)
            
            if provider_usage['request_count'] > 0:
                with st.expander(f"{provider.upper()} - ${provider_usage['total_cost']:.2f}"):
                    col1, col2 = st.columns(2)
                    col1.metric("Tokens", f"{provider_usage['total_tokens']:,}")
                    col2.metric("Requests", f"{provider_usage['request_count']:,}")

# Example 5: Database health check
def database_health_check():
    """Example of database health check."""
    st.sidebar.header("Database Status")
    
    db_manager = container.database.db_manager()
    
    if db_manager.health_check():
        st.sidebar.success("✅ Database Connected")
    else:
        st.sidebar.error("❌ Database Disconnected")

# Main app
def main():
    st.title("PCA Agent - PostgreSQL Integration Example")
    
    # Database health check in sidebar
    database_health_check()
    
    # Navigation
    page = st.sidebar.selectbox(
        "Select Example",
        [
            "Import Campaigns",
            "Query Campaigns",
            "Save Analysis",
            "View LLM Usage"
        ]
    )
    
    # Route to examples
    if page == "Import Campaigns":
        import_campaigns_example()
    elif page == "Query Campaigns":
        query_campaigns_example()
    elif page == "Save Analysis":
        save_analysis_example()
    elif page == "View LLM Usage":
        view_llm_usage_example()

if __name__ == "__main__":
    main()
