"""
MCP (Model Context Protocol) Integration for PCA Agent

Provides:
- Phase 1: Unified data access layer for all sources
- Phase 2: MCP tools for LLM to call directly
- Phase 3: Enhanced RAG with live data integration
- Streamlit helpers: Synchronous wrappers for Streamlit compatibility
"""

from src.mcp.resource_server import PCAResourceServer, get_mcp_server
from src.mcp.client import PCAMCPClient, connect_mcp, read_campaign_data
from src.mcp.tools import PCATools
from src.mcp.rag_integration import MCPEnhancedRAG, create_enhanced_rag
from src.mcp.streamlit_helpers import (
    StreamlitMCPClient,
    StreamlitEnhancedRAG,
    StreamlitMCPTools,
    init_mcp_client,
    init_enhanced_rag,
    init_mcp_tools,
    connect_database_mcp
)

__all__ = [
    # Async (for Python scripts)
    "PCAResourceServer",
    "get_mcp_server",
    "PCAMCPClient",
    "connect_mcp",
    "read_campaign_data",
    "PCATools",
    "MCPEnhancedRAG",
    "create_enhanced_rag",
    
    # Sync (for Streamlit)
    "StreamlitMCPClient",
    "StreamlitEnhancedRAG",
    "StreamlitMCPTools",
    "init_mcp_client",
    "init_enhanced_rag",
    "init_mcp_tools",
    "connect_database_mcp",
]
