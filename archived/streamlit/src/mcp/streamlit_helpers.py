"""
Streamlit-compatible helpers for MCP integration
Wraps async MCP calls for use in Streamlit (which doesn't support async/await)
"""

import asyncio
import pandas as pd
from typing import Optional, Dict, Any, List
from loguru import logger

from src.mcp.client import PCAMCPClient
from src.mcp.resource_server import get_mcp_server
from src.mcp.rag_integration import MCPEnhancedRAG
from src.mcp.tools import PCATools


class StreamlitMCPClient:
    """Synchronous wrapper for MCP client for Streamlit compatibility."""
    
    def __init__(self):
        """Initialize Streamlit-compatible MCP client."""
        self._client: Optional[PCAMCPClient] = None
        self._loop = None
        logger.info("Streamlit MCP Client initialized")
    
    def connect(self) -> bool:
        """Connect to MCP server (synchronous)."""
        try:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            
            self._client = PCAMCPClient()
            self._loop.run_until_complete(self._client.connect())
            
            logger.success("Connected to MCP server")
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False
    
    def list_resources(self) -> List:
        """List available resources (synchronous)."""
        if not self._client:
            raise RuntimeError("Not connected. Call connect() first.")
        
        return self._loop.run_until_complete(self._client.list_resources())
    
    def query_database(
        self,
        connection_id: str,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """Query database (synchronous)."""
        if not self._client:
            raise RuntimeError("Not connected. Call connect() first.")
        
        return self._loop.run_until_complete(
            self._client.query_database(connection_id, table, filters, limit)
        )
    
    def load_from_cloud(
        self,
        source: str,
        path: str,
        **kwargs
    ) -> pd.DataFrame:
        """Load from cloud storage (synchronous)."""
        if not self._client:
            raise RuntimeError("Not connected. Call connect() first.")
        
        return self._loop.run_until_complete(
            self._client.load_from_cloud(source, path, **kwargs)
        )
    
    def get_analytics_metrics(self) -> Dict[str, Any]:
        """Get analytics metrics (synchronous)."""
        if not self._client:
            raise RuntimeError("Not connected. Call connect() first.")
        
        return self._loop.run_until_complete(
            self._client.get_analytics_metrics()
        )
    
    def disconnect(self):
        """Disconnect from MCP server."""
        if self._client:
            self._loop.run_until_complete(self._client.disconnect())
            self._loop.close()
            self._client = None
            logger.info("Disconnected from MCP server")


class StreamlitEnhancedRAG:
    """Synchronous wrapper for Enhanced RAG for Streamlit compatibility."""
    
    def __init__(self):
        """Initialize Streamlit-compatible Enhanced RAG."""
        self._rag: Optional[MCPEnhancedRAG] = None
        self._loop = None
        logger.info("Streamlit Enhanced RAG initialized")
    
    def connect(self) -> bool:
        """Connect to MCP server (synchronous)."""
        try:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            
            self._rag = MCPEnhancedRAG()
            self._loop.run_until_complete(self._rag.connect())
            
            logger.success("Enhanced RAG connected")
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False
    
    def retrieve_context(
        self,
        query: str,
        top_k: int = 5,
        include_live_data: bool = True
    ) -> List[Dict[str, Any]]:
        """Retrieve context (synchronous)."""
        if not self._rag:
            raise RuntimeError("Not connected. Call connect() first.")
        
        return self._loop.run_until_complete(
            self._rag.retrieve_context(query, top_k, include_live_data)
        )
    
    def generate_enhanced_summary(
        self,
        query: str,
        campaign_data: Optional[pd.DataFrame] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """Generate enhanced summary (synchronous)."""
        if not self._rag:
            raise RuntimeError("Not connected. Call connect() first.")
        
        return self._loop.run_until_complete(
            self._rag.generate_enhanced_summary(query, campaign_data, top_k)
        )
    
    def get_contextual_recommendations(
        self,
        campaign_data: pd.DataFrame,
        focus_area: str = "all"
    ) -> List[Dict[str, Any]]:
        """Get contextual recommendations (synchronous)."""
        if not self._rag:
            raise RuntimeError("Not connected. Call connect() first.")
        
        return self._loop.run_until_complete(
            self._rag.get_contextual_recommendations(campaign_data, focus_area)
        )
    
    def disconnect(self):
        """Disconnect from MCP server."""
        if self._rag:
            self._loop.run_until_complete(self._rag.disconnect())
            self._loop.close()
            self._rag = None
            logger.info("Enhanced RAG disconnected")


class StreamlitMCPTools:
    """Synchronous wrapper for MCP tools for Streamlit compatibility."""
    
    def __init__(self):
        """Initialize Streamlit-compatible MCP tools."""
        self._tools = PCATools()
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        logger.info("Streamlit MCP Tools initialized")
    
    def get_tool_definitions(self) -> List:
        """Get tool definitions."""
        return self._tools.get_tool_definitions()
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool (synchronous)."""
        return self._loop.run_until_complete(
            self._tools.execute_tool(tool_name, arguments)
        )
    
    def query_campaigns(self, **kwargs) -> Dict[str, Any]:
        """Query campaigns tool."""
        return self.execute_tool("query_campaigns", kwargs)
    
    def get_campaign_metrics(self, **kwargs) -> Dict[str, Any]:
        """Get campaign metrics tool."""
        return self.execute_tool("get_campaign_metrics", kwargs)
    
    def compare_platforms(self, **kwargs) -> Dict[str, Any]:
        """Compare platforms tool."""
        return self.execute_tool("compare_platforms", kwargs)
    
    def identify_opportunities(self, **kwargs) -> Dict[str, Any]:
        """Identify opportunities tool."""
        return self.execute_tool("identify_opportunities", kwargs)
    
    def get_recommendations(self, **kwargs) -> Dict[str, Any]:
        """Get recommendations tool."""
        return self.execute_tool("get_recommendations", kwargs)


# Convenience functions for Streamlit
def init_mcp_client() -> StreamlitMCPClient:
    """Initialize MCP client for Streamlit."""
    client = StreamlitMCPClient()
    client.connect()
    return client


def init_enhanced_rag() -> StreamlitEnhancedRAG:
    """Initialize Enhanced RAG for Streamlit."""
    rag = StreamlitEnhancedRAG()
    rag.connect()
    return rag


def init_mcp_tools() -> StreamlitMCPTools:
    """Initialize MCP tools for Streamlit."""
    return StreamlitMCPTools()


# Database connection helper
def connect_database_mcp(
    connection_id: str,
    db_type: str,
    **kwargs
) -> Dict[str, Any]:
    """Connect to database via MCP (synchronous)."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        server = get_mcp_server()
        result = loop.run_until_complete(
            server.connect_database(connection_id, db_type, **kwargs)
        )
        return result
    finally:
        loop.close()
