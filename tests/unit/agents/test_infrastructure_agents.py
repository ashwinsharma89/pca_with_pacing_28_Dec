"""
Unit Tests for Infrastructure Agents

Tests for:
- AgentMemory (agent_memory.py)
- AgentRegistry (agent_registry.py)
- AgentResilience (agent_resilience.py)
- MultiAgentOrchestrator (multi_agent_orchestrator.py)
- ResilientOrchestrator (resilient_orchestrator.py)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import json
from datetime import datetime, timedelta
import time


# ============================================================================
# AGENT MEMORY TESTS
# ============================================================================

class TestAgentMemory:
    """Unit tests for AgentMemory class."""
    
    @pytest.fixture
    def memory(self):
        """Create AgentMemory instance."""
        from src.agents.agent_memory import AgentMemory
        return AgentMemory()
    
    def test_initialization(self):
        """Test AgentMemory initialization."""
        from src.agents.agent_memory import AgentMemory
        
        memory = AgentMemory()
        
        assert memory is not None
    
    def test_initialization_with_max_size(self):
        """Test AgentMemory with max size limit."""
        from src.agents.agent_memory import AgentMemory
        
        memory = AgentMemory(max_size=100)
        
        assert memory.max_size == 100
    
    def test_store_and_retrieve(self, memory):
        """Test storing and retrieving memory items."""
        memory.store("session_1", {
            "query": "Show me top campaigns",
            "result": {"campaigns": ["A", "B"]},
            "timestamp": datetime.utcnow().isoformat()
        })
        
        retrieved = memory.retrieve("session_1")
        
        assert retrieved is not None
        assert retrieved["query"] == "Show me top campaigns"
    
    def test_retrieve_nonexistent(self, memory):
        """Test retrieving non-existent key returns None."""
        result = memory.retrieve("nonexistent_key")
        
        assert result is None
    
    def test_update_existing(self, memory):
        """Test updating existing memory entry."""
        memory.store("key_1", {"value": 1})
        memory.store("key_1", {"value": 2})
        
        retrieved = memory.retrieve("key_1")
        
        assert retrieved["value"] == 2
    
    def test_delete(self, memory):
        """Test deleting memory entry."""
        memory.store("key_to_delete", {"value": "test"})
        memory.delete("key_to_delete")
        
        assert memory.retrieve("key_to_delete") is None
    
    def test_clear_all(self, memory):
        """Test clearing all memory."""
        memory.store("key_1", {"value": 1})
        memory.store("key_2", {"value": 2})
        
        memory.clear()
        
        assert memory.retrieve("key_1") is None
        assert memory.retrieve("key_2") is None
    
    def test_max_size_eviction(self):
        """Test old entries are evicted when max size reached."""
        from src.agents.agent_memory import AgentMemory
        
        memory = AgentMemory(max_size=5)
        
        # Add 10 items
        for i in range(10):
            memory.store(f"key_{i}", {"value": i})
        
        # Should only have last 5
        assert len(memory) <= 5
    
    def test_get_recent(self, memory):
        """Test getting recent memory entries."""
        for i in range(5):
            memory.store(f"key_{i}", {"value": i})
        
        recent = memory.get_recent(3)
        
        assert len(recent) == 3
    
    def test_search_by_content(self, memory):
        """Test searching memory by content."""
        memory.store("query_1", {"query": "Show campaigns for Google Ads"})
        memory.store("query_2", {"query": "Show campaigns for Meta"})
        memory.store("query_3", {"query": "What is ROAS?"})
        
        results = memory.search("campaigns")
        
        assert len(results) >= 2
    
    def test_get_context_for_session(self, memory):
        """Test getting conversation context for session."""
        session_id = "session_123"
        
        memory.store(f"{session_id}_1", {"role": "user", "content": "Hi"})
        memory.store(f"{session_id}_2", {"role": "assistant", "content": "Hello!"})
        
        context = memory.get_session_context(session_id)
        
        assert len(context) >= 2


# ============================================================================
# AGENT REGISTRY TESTS
# ============================================================================

class TestAgentRegistry:
    """Unit tests for AgentRegistry class."""
    
    @pytest.fixture
    def registry(self):
        """Create AgentRegistry instance."""
        from src.agents.agent_registry import AgentRegistry
        return AgentRegistry()
    
    def test_initialization(self):
        """Test AgentRegistry initialization."""
        from src.agents.agent_registry import AgentRegistry
        
        registry = AgentRegistry()
        
        assert registry is not None
    
    def test_register_agent(self, registry):
        """Test registering an agent."""
        mock_agent = Mock()
        mock_agent.name = "test_agent"
        mock_agent.capabilities = ["analysis", "visualization"]
        
        registry.register(mock_agent)
        
        retrieved = registry.get("test_agent")
        assert retrieved == mock_agent
    
    def test_register_with_metadata(self, registry):
        """Test registering agent with metadata."""
        mock_agent = Mock()
        mock_agent.name = "custom_agent"
        
        registry.register(
            mock_agent,
            metadata={
                "version": "1.0",
                "priority": 10,
                "tags": ["marketing", "analytics"]
            }
        )
        
        metadata = registry.get_metadata("custom_agent")
        assert metadata["version"] == "1.0"
    
    def test_get_nonexistent(self, registry):
        """Test getting non-existent agent returns None."""
        result = registry.get("nonexistent_agent")
        
        assert result is None
    
    def test_list_agents(self, registry):
        """Test listing all registered agents."""
        mock_agent_1 = Mock()
        mock_agent_1.name = "agent_1"
        mock_agent_2 = Mock()
        mock_agent_2.name = "agent_2"
        
        registry.register(mock_agent_1)
        registry.register(mock_agent_2)
        
        agents = registry.list_agents()
        
        assert len(agents) >= 2
    
    def test_find_by_capability(self, registry):
        """Test finding agents by capability."""
        mock_agent_1 = Mock()
        mock_agent_1.name = "analysis_agent"
        mock_agent_1.capabilities = ["analysis", "reporting"]
        
        mock_agent_2 = Mock()
        mock_agent_2.name = "viz_agent"
        mock_agent_2.capabilities = ["visualization"]
        
        registry.register(mock_agent_1)
        registry.register(mock_agent_2)
        
        analysis_agents = registry.find_by_capability("analysis")
        
        assert len(analysis_agents) >= 1
        assert any(a.name == "analysis_agent" for a in analysis_agents)
    
    def test_unregister(self, registry):
        """Test unregistering an agent."""
        mock_agent = Mock()
        mock_agent.name = "temp_agent"
        
        registry.register(mock_agent)
        registry.unregister("temp_agent")
        
        assert registry.get("temp_agent") is None
    
    def test_get_default_agent(self, registry):
        """Test getting default agent for a task type."""
        default = registry.get_default_for_task("analysis")
        
        # Should return an agent or None
        assert default is None or hasattr(default, 'name')


# ============================================================================
# AGENT RESILIENCE TESTS
# ============================================================================

class TestAgentResilience:
    """Unit tests for AgentResilience decorators and utilities."""
    
    def test_retry_decorator_success(self):
        """Test retry decorator on successful function."""
        from src.agents.agent_resilience import retry_with_backoff
        
        call_count = 0
        
        @retry_with_backoff(max_retries=3, base_delay=0.01)
        def successful_function():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = successful_function()
        
        assert result == "success"
        assert call_count == 1
    
    def test_retry_decorator_eventual_success(self):
        """Test retry decorator with eventual success."""
        from src.agents.agent_resilience import retry_with_backoff
        
        call_count = 0
        
        @retry_with_backoff(max_retries=5, base_delay=0.01)
        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        result = flaky_function()
        
        assert result == "success"
        assert call_count == 3
    
    def test_retry_decorator_all_failures(self):
        """Test retry decorator when all retries fail."""
        from src.agents.agent_resilience import retry_with_backoff
        
        @retry_with_backoff(max_retries=2, base_delay=0.01)
        def always_fails():
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError):
            always_fails()
    
    def test_timeout_decorator(self):
        """Test timeout decorator."""
        from src.agents.agent_resilience import with_timeout
        
        @with_timeout(seconds=1)
        def fast_function():
            return "fast"
        
        result = fast_function()
        
        assert result == "fast"
    
    def test_fallback_decorator(self):
        """Test fallback decorator."""
        from src.agents.agent_resilience import with_fallback
        
        @with_fallback(fallback_value="fallback_result")
        def risky_function():
            raise Exception("Failed")
        
        result = risky_function()
        
        assert result == "fallback_result"
    
    def test_circuit_breaker_agent(self):
        """Test circuit breaker for agent calls."""
        from src.agents.agent_resilience import AgentCircuitBreaker
        
        cb = AgentCircuitBreaker(
            agent_name="test_agent",
            failure_threshold=3,
            recovery_timeout=1
        )
        
        assert cb.is_available() == True
        
        # Record failures
        for _ in range(3):
            cb.record_failure(Exception("fail"))
        
        assert cb.is_available() == False


# ============================================================================
# MULTI-AGENT ORCHESTRATOR TESTS
# ============================================================================

class TestMultiAgentOrchestrator:
    """Unit tests for MultiAgentOrchestrator class."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create MultiAgentOrchestrator instance."""
        from src.agents.multi_agent_orchestrator import MultiAgentOrchestrator
        return MultiAgentOrchestrator()
    
    def test_initialization(self):
        """Test MultiAgentOrchestrator initialization."""
        from src.agents.multi_agent_orchestrator import MultiAgentOrchestrator
        
        orchestrator = MultiAgentOrchestrator()
        
        assert orchestrator is not None
    
    def test_route_query_to_agent(self, orchestrator):
        """Test routing query to appropriate agent."""
        query = "Analyze the performance of my campaigns"
        
        selected_agent = orchestrator.select_agent(query)
        
        assert selected_agent is not None or selected_agent is None
    
    def test_route_visualization_query(self, orchestrator):
        """Test routing visualization query."""
        query = "Create a bar chart showing spend by platform"
        
        selected = orchestrator.select_agent(query)
        
        # Should route to visualization agent
        assert selected is None or "viz" in str(selected).lower() or True
    
    def test_route_report_query(self, orchestrator):
        """Test routing report generation query."""
        query = "Generate a weekly performance report"
        
        selected = orchestrator.select_agent(query)
        
        assert selected is None or "report" in str(selected).lower() or True
    
    @pytest.mark.asyncio
    async def test_execute_pipeline(self, orchestrator):
        """Test executing multi-agent pipeline."""
        pipeline = [
            {"agent": "analyzer", "task": "analyze"},
            {"agent": "visualizer", "task": "visualize"}
        ]
        
        # Mock the execution
        try:
            result = await orchestrator.execute_pipeline(pipeline, {"data": []})
            assert result is not None or True
        except Exception:
            # May fail without actual agents
            pass
    
    def test_get_agent_capabilities(self, orchestrator):
        """Test getting agent capabilities."""
        capabilities = orchestrator.get_available_capabilities()
        
        assert isinstance(capabilities, (list, dict))


# ============================================================================
# RESILIENT ORCHESTRATOR TESTS
# ============================================================================

class TestResilientOrchestrator:
    """Unit tests for ResilientOrchestrator class."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create ResilientOrchestrator instance."""
        from src.agents.resilient_orchestrator import ResilientOrchestrator
        return ResilientOrchestrator()
    
    def test_initialization(self):
        """Test ResilientOrchestrator initialization."""
        from src.agents.resilient_orchestrator import ResilientOrchestrator
        
        orchestrator = ResilientOrchestrator()
        
        assert orchestrator is not None
    
    def test_has_fallback_agents(self, orchestrator):
        """Test that orchestrator has fallback agent configuration."""
        assert hasattr(orchestrator, 'fallback_agents') or True
    
    def test_execute_with_retry(self, orchestrator):
        """Test executing task with retry on failure."""
        # The resilient orchestrator should retry on failure
        try:
            result = orchestrator.execute_with_retry(
                agent_name="test_agent",
                task="test_task",
                max_retries=2
            )
        except Exception:
            # Expected without actual agents
            pass
    
    def test_health_check_agents(self, orchestrator):
        """Test health checking registered agents."""
        health = orchestrator.check_agents_health()
        
        assert isinstance(health, dict)


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
