"""
Example: Using MCP in Streamlit

This shows how to integrate MCP features into your Streamlit app
using the synchronous wrappers.
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.mcp.streamlit_helpers import (
    init_mcp_client,
    init_enhanced_rag,
    init_mcp_tools,
    connect_database_mcp
)

st.set_page_config(page_title="MCP Integration Demo", page_icon="🔌", layout="wide")

st.title("🔌 MCP Integration Demo")
st.markdown("Demonstrating Model Context Protocol in Streamlit")

# Tabs for different features
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Data Access",
    "🛠️ MCP Tools", 
    "🔬 Enhanced RAG",
    "🗄️ Database Connection"
])

# Tab 1: Data Access
with tab1:
    st.header("📊 MCP Data Access")
    
    st.markdown("""
    MCP provides unified access to all data sources through standardized URIs.
    """)
    
    if st.button("Initialize MCP Client"):
        with st.spinner("Connecting to MCP server..."):
            try:
                if 'mcp_client' not in st.session_state:
                    st.session_state.mcp_client = init_mcp_client()
                st.success("✅ Connected to MCP server!")
            except Exception as e:
                st.error(f"❌ Connection failed: {e}")
    
    if 'mcp_client' in st.session_state:
        st.success("🟢 MCP Client Active")
        
        # List resources
        if st.button("List Available Resources"):
            try:
                resources = st.session_state.mcp_client.list_resources()
                st.write(f"Found {len(resources)} resources:")
                for resource in resources[:10]:
                    st.markdown(f"- **{resource.name}**: `{resource.uri}`")
            except Exception as e:
                st.error(f"Error: {e}")
        
        # Example: Load from cloud (demo)
        st.markdown("---")
        st.subheader("Load from Cloud Storage")
        
        col1, col2 = st.columns(2)
        with col1:
            source = st.selectbox("Source", ["s3", "azure", "gcs"])
        with col2:
            path = st.text_input("Path", placeholder="bucket/path/to/file.csv")
        
        if st.button("Load Data"):
            if path:
                try:
                    with st.spinner(f"Loading from {source}..."):
                        df = st.session_state.mcp_client.load_from_cloud(source, path)
                    st.success(f"✅ Loaded {len(df)} rows")
                    st.dataframe(df.head())
                except Exception as e:
                    st.warning(f"Demo error (expected): {str(e)[:100]}")
            else:
                st.warning("Please enter a path")

# Tab 2: MCP Tools
with tab2:
    st.header("🛠️ MCP Tools")
    
    st.markdown("""
    LLMs can call these tools directly for reliable campaign analysis.
    """)
    
    if st.button("Initialize MCP Tools"):
        with st.spinner("Loading tools..."):
            try:
                if 'mcp_tools' not in st.session_state:
                    st.session_state.mcp_tools = init_mcp_tools()
                st.success("✅ MCP Tools loaded!")
            except Exception as e:
                st.error(f"❌ Failed: {e}")
    
    if 'mcp_tools' in st.session_state:
        st.success("🟢 MCP Tools Active")
        
        # Show available tools
        with st.expander("📋 Available Tools"):
            tools = st.session_state.mcp_tools.get_tool_definitions()
            for tool in tools:
                st.markdown(f"**{tool.name}**")
                st.caption(tool.description)
        
        # Example: Query campaigns tool
        st.markdown("---")
        st.subheader("Try: Query Campaigns Tool")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            metric = st.selectbox("Metric", ["roas", "spend", "conversions", "ctr"])
        with col2:
            period = st.selectbox("Period", ["7d", "30d", "90d"])
        with col3:
            platform = st.text_input("Platform (optional)", placeholder="Meta")
        
        if st.button("Execute Tool"):
            try:
                with st.spinner("Executing query_campaigns tool..."):
                    result = st.session_state.mcp_tools.query_campaigns(
                        metric=metric,
                        period=period,
                        platform=platform if platform else None,
                        limit=10
                    )
                st.success("✅ Tool executed!")
                st.json(result)
            except Exception as e:
                st.error(f"Error: {e}")

# Tab 3: Enhanced RAG
with tab3:
    st.header("🔬 Enhanced RAG with Live Data")
    
    st.markdown("""
    Enhanced RAG combines static knowledge base with live campaign data
    for richer, more relevant insights.
    """)
    
    if st.button("Initialize Enhanced RAG"):
        with st.spinner("Connecting Enhanced RAG..."):
            try:
                if 'enhanced_rag' not in st.session_state:
                    st.session_state.enhanced_rag = init_enhanced_rag()
                st.success("✅ Enhanced RAG connected!")
            except Exception as e:
                st.error(f"❌ Connection failed: {e}")
    
    if 'enhanced_rag' in st.session_state:
        st.success("🟢 Enhanced RAG Active")
        
        # Context retrieval
        st.subheader("Retrieve Multi-Source Context")
        
        query = st.text_area(
            "Query",
            placeholder="How to optimize Meta campaigns for Q4?",
            height=100
        )
        
        col1, col2 = st.columns(2)
        with col1:
            top_k = st.slider("Number of contexts", 1, 10, 5)
        with col2:
            include_live = st.checkbox("Include live data", value=True)
        
        if st.button("Retrieve Context"):
            if query:
                try:
                    with st.spinner("Retrieving context from multiple sources..."):
                        contexts = st.session_state.enhanced_rag.retrieve_context(
                            query=query,
                            top_k=top_k,
                            include_live_data=include_live
                        )
                    
                    st.success(f"✅ Retrieved {len(contexts)} contexts")
                    
                    for i, ctx in enumerate(contexts, 1):
                        with st.expander(f"Context {i}: {ctx['source']} ({ctx['type']})"):
                            st.markdown(f"**Score:** {ctx['score']:.2f}")
                            st.markdown(f"**Content:** {ctx['content'][:200]}...")
                            st.json(ctx['metadata'])
                
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Please enter a query")
        
        # Enhanced summary
        st.markdown("---")
        st.subheader("Generate Enhanced Summary")
        
        summary_query = st.text_input(
            "Summary Query",
            placeholder="Analyze current campaign performance"
        )
        
        # Sample data for demo
        if st.checkbox("Use sample campaign data"):
            sample_data = pd.DataFrame({
                'Campaign': ['Campaign A', 'Campaign B', 'Campaign C'],
                'Platform': ['Meta', 'Google', 'TikTok'],
                'Spend': [5000, 8000, 3000],
                'Conversions': [250, 320, 180],
                'ROAS': [2.5, 2.8, 3.2]
            })
            st.dataframe(sample_data)
            
            if st.button("Generate Summary"):
                try:
                    with st.spinner("Generating enhanced summary..."):
                        summary = st.session_state.enhanced_rag.generate_enhanced_summary(
                            query=summary_query,
                            campaign_data=sample_data,
                            top_k=5
                        )
                    
                    st.success("✅ Summary generated!")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Knowledge Base Sources", summary['sources']['knowledge_base'])
                    with col2:
                        st.metric("Live Data Sources", summary['sources']['live_data'])
                    
                    st.markdown("### Summary")
                    st.info(summary['summary'])
                    
                    with st.expander("View Context Sources"):
                        for ctx in summary['contexts'][:5]:
                            st.markdown(f"- **{ctx['source']}** ({ctx['type']}): Score {ctx['score']:.2f}")
                
                except Exception as e:
                    st.error(f"Error: {e}")

# Tab 4: Database Connection
with tab4:
    st.header("🗄️ Database Connection via MCP")
    
    st.markdown("""
    Connect to databases and expose them as MCP resources.
    """)
    
    db_type = st.selectbox(
        "Database Type",
        ["sqlite", "postgresql", "mysql", "snowflake", "bigquery"]
    )
    
    if db_type == "sqlite":
        st.subheader("SQLite Connection")
        
        file_path = st.text_input("Database File Path", placeholder="data/campaigns.db")
        connection_id = st.text_input("Connection ID", value="sqlite_local")
        
        if st.button("Connect to SQLite"):
            if file_path:
                try:
                    with st.spinner("Connecting..."):
                        result = connect_database_mcp(
                            connection_id=connection_id,
                            db_type="sqlite",
                            file_path=file_path
                        )
                    
                    if result['success']:
                        st.success(f"✅ Connected! Found {len(result['tables'])} tables")
                        st.write("Tables:", result['tables'])
                    else:
                        st.error(f"❌ Connection failed: {result['error']}")
                
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Please provide file path")
    
    elif db_type == "snowflake":
        st.subheader("Snowflake Connection")
        
        col1, col2 = st.columns(2)
        with col1:
            account = st.text_input("Account", placeholder="xy12345.us-east-1")
            database = st.text_input("Database", placeholder="CAMPAIGN_DB")
            warehouse = st.text_input("Warehouse", placeholder="COMPUTE_WH")
        with col2:
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            connection_id = st.text_input("Connection ID", value="snowflake_prod")
        
        if st.button("Connect to Snowflake"):
            if all([account, database, username, password, warehouse]):
                try:
                    with st.spinner("Connecting to Snowflake..."):
                        result = connect_database_mcp(
                            connection_id=connection_id,
                            db_type="snowflake",
                            account=account,
                            database=database,
                            username=username,
                            password=password,
                            warehouse=warehouse
                        )
                    
                    if result['success']:
                        st.success(f"✅ Connected! Found {len(result['tables'])} tables")
                        with st.expander("View Tables"):
                            for table in result['tables']:
                                st.markdown(f"- {table}")
                    else:
                        st.error(f"❌ Connection failed: {result['error']}")
                
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Please fill in all fields")
    
    else:
        st.info(f"Connection form for {db_type} - implement as needed")

# Sidebar info
with st.sidebar:
    st.markdown("### 🔌 MCP Integration")
    st.markdown("""
    This demo shows how to use MCP features in Streamlit:
    
    - **Data Access**: Unified access to all sources
    - **MCP Tools**: LLM-callable analytics tools
    - **Enhanced RAG**: Multi-source context
    - **Database**: Connect and query databases
    """)
    
    st.markdown("---")
    
    # Status indicators
    st.markdown("### Status")
    if 'mcp_client' in st.session_state:
        st.success("🟢 MCP Client")
    else:
        st.warning("⚪ MCP Client")
    
    if 'mcp_tools' in st.session_state:
        st.success("🟢 MCP Tools")
    else:
        st.warning("⚪ MCP Tools")
    
    if 'enhanced_rag' in st.session_state:
        st.success("🟢 Enhanced RAG")
    else:
        st.warning("⚪ Enhanced RAG")
