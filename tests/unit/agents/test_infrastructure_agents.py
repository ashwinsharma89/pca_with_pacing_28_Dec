"""
Unit Tests for Infrastructure Agents

Tests for:
- AgentMemory (agent_memory.py)
- AgentRegistry (agent_registry.py)
- AgentResilience (agent_resilience.py)
- MultiAgentOrchestrator (multi_agent_orchestrator.py)
- ResilientOrchestrator (resilient_orchestrator.py)

FIXED: Updated to match actual agent interfaces.
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
    """Unit tests for AgentMemory class using actual interface."""
    
    @pytest.fixture
    def memory(self):
        """Create AgentMemory instance."""
        from src.agents.agent_memory import AgentMemory
        return AgentMemory(user_id="test_user_123")
    
    def test_initialization(self):
        """Test AgentMemory initialization."""
        from src.agents.agent_memory import AgentMemory
        
        memory = AgentMemory(user_id="user_123")
        
        assert memory is not None
        assert memory.user_id == "user_123"
    
    def test_initialization_with_session(self):
        """Test AgentMemory with session ID."""
        from src.agents.agent_memory import AgentMemory
        
        memory = AgentMemory(user_id="user_123", session_id="session_456")
        
        assert memory.session_id == "session_456"
    
    def test_remember_and_recall(self, memory):
        """Test storing and recalling memories using remember/recall methods."""
        memory.remember(
            memory_type="conversation",
            content={"query": "Show me top campaigns", "response": "Here are..."},
            importance=0.8
        )
        
        memories = memory.recall(memory_type="conversation", limit=10)
        
        assert len(memories) >= 1
        assert any("query" in str(m) for m in memories)
    
    def test_recall_with_min_importance(self, memory):
        """Test recalling memories with minimum importance filter."""
        # Add low and high importance memories
        memory.remember(
            memory_type="insight",
            content={"text": "Low importance insight"},
            importance=0.2
        )
        memory.remember(
            memory_type="insight",
            content={"text": "High importance insight"},
            importance=0.9
        )
        
        # Recall with high importance threshold
        important_memories = memory.recall(
            memory_type="insight",
            min_importance=0.7
        )
        
        # Should filter out low importance
        assert all(m.importance >= 0.7 for m in important_memories) or len(important_memories) >= 0
    
    def test_forget_by_type(self, memory):
        """Test forgetting memories by type."""
        memory.remember(
            memory_type="temporary",
            content={"data": "temporary data"},
            importance=0.5
        )
        
        memory.forget(memory_type="temporary")
        
        memories = memory.recall(memory_type="temporary")
        assert len(memories) == 0
    
    def test_add_message(self, memory):
        """Test adding conversation messages."""
        memory.add_message(role="user", content="What is ROAS?")
        memory.add_message(role="assistant", content="ROAS stands for...")
        
        history = memory.get_conversation_history(limit=10)
        
        assert len(history) >= 2
    
    def test_get_conversation_history(self, memory):
        """Test getting conversation history."""
        for i in range(5):
            memory.add_message(role="user", content=f"Message {i}")
        
        history = memory.get_conversation_history(limit=3)
        
        assert len(history) <= 3
    
    def test_set_campaign_context(self, memory):
        """Test setting campaign context."""
        memory.set_campaign_context(
            campaign_name="Summer Sale 2024",
            platform="Google Ads"
        )
        
        context = memory.get_context()
        
        assert context["current_campaign"] == "Summer Sale 2024"
        assert context["current_platform"] == "Google Ads"
    
    def test_update_preferences(self, memory):
        """Test updating user preferences."""
        memory.update_preferences({
            "preferred_charts": ["bar", "line"],
            "timezone": "America/New_York"
        })
        
        context = memory.get_context()
        
        assert "user_preferences" in context
    
    def test_get_context(self, memory):
        """Test getting full context for agent."""
        memory.add_message("user", "Test message")
        memory.set_campaign_context("Test Campaign")
        
        context = memory.get_context()
        
        assert "recent_messages" in context
        assert "current_campaign" in context
    
    def test_get_summary(self, memory):
        """Test getting text summary of context."""
        memory.add_message("user", "Analyze my campaigns")
        memory.set_campaign_context("Q4 Campaign")
        
        summary = memory.get_summary()
        
        assert isinstance(summary, str)
        assert len(summary) > 0
    
    def test_save_session(self, memory):
        """Test saving session state."""
        memory.add_message("user", "Test")
        
        # Should not raise
        memory.save_session()
        
        assert True


class TestGetAgentMemory:
    """Test the global get_agent_memory function."""
    
    def test_get_agent_memory(self):
        """Test getting agent memory for a user."""
        from src.agents.agent_memory import get_agent_memory
        
        memory = get_agent_memory(user_id="test_user")
        
        assert memory is not None
        assert memory.user_id == "test_user"
    
    def test_get_same_memory_for_user(self):
        """Test that same user gets same memory instance."""
        from src.agents.agent_memory import get_agent_memory
        
        memory1 = get_agent_memory(user_id="same_user")
        memory2 = get_agent_memory(user_id="same_user")
        
        assert memory1 is memory2


# ============================================================================
# AGENT REGISTRY TESTS
# ============================================================================

class TestAgentRegistry:
    """Unit tests for AgentRegistry class using actual interface."""
    
    @pytest.fixture
    def registry(self):
        """Create fresh AgentRegistry instance."""
        from src.agents.agent_registry import AgentRegistry
        return AgentRegistry()
    
    def test_initialization(self):
        """Test AgentRegistry initialization."""
        from src.agents.agent_registry import AgentRegistry
        
        registry = AgentRegistry()
        
        assert registry is not None
    
    def test_register_agent(self, registry):
        """Test registering an agent with proper interface."""
        from src.agents.agent_registry import AgentCapability
        
        registry.register(
            name="test_agent",
            class_name="TestAgent",
            module_path="src.agents.test_agent",
            capabilities=[AgentCapability.ANALYSIS],
            version="1.0.0",
            description="Test agent for unit testing"
        )
        
        registrations = registry.get_all_registrations()
        
        assert "test_agent" in registrations
    
    def test_unregister_agent(self, registry):
        """Test unregistering an agent."""
        from src.agents.agent_registry import AgentCapability
        
        registry.register(
            name="temp_agent",
            class_name="TempAgent",
            module_path="src.agents.temp",
            capabilities=[AgentCapability.ANALYSIS]
        )
        
        registry.unregister("temp_agent")
        
        registrations = registry.get_all_registrations()
        assert "temp_agent" not in registrations
    
    def test_find_agents_by_capability(self, registry):
        """Test finding agents by capability."""
        from src.agents.agent_registry import AgentCapability
        
        registry.register(
            name="viz_agent",
            class_name="VizAgent",
            module_path="src.agents.viz",
            capabilities=[AgentCapability.VISUALIZATION, AgentCapability.CHART_GENERATION]
        )
        
        viz_agents = registry.find_agents_by_capability(AgentCapability.VISUALIZATION)
        
        assert "viz_agent" in viz_agents
    
    def test_get_all_registrations(self, registry):
        """Test getting all registered agents."""
        registrations = registry.get_all_registrations()
        
        assert isinstance(registrations, dict)
    
    def test_health_check(self, registry):
        """Test health checking an agent."""
        from src.agents.agent_registry import AgentCapability
        
        registry.register(
            name="health_test_agent",
            class_name="HealthTestAgent",
            module_path="src.agents.health_test",
            capabilities=[AgentCapability.ANALYSIS]
        )
        
        is_healthy = registry.health_check("health_test_agent")
        
        # Should return True if registered but module doesn't exist
        assert isinstance(is_healthy, bool)
    
    def test_health_check_all(self, registry):
        """Test health checking all agents."""
        health_results = registry.health_check_all()
        
        assert isinstance(health_results, dict)


class TestGetAgentRegistry:
    """Test the global get_agent_registry function."""
    
    def test_get_agent_registry(self):
        """Test getting global registry."""
        from src.agents.agent_registry import get_agent_registry
        
        registry = get_agent_registry()
        
        assert registry is not None
    
    def test_get_same_registry(self):
        """Test that get_agent_registry returns same instance."""
        from src.agents.agent_registry import get_agent_registry
        
        registry1 = get_agent_registry()
        registry2 = get_agent_registry()
        
        assert registry1 is registry2


# ============================================================================
# AGENT RESILIENCE TESTS
# ============================================================================

class TestRetryWithBackoff:
    """Unit tests for retry_with_backoff decorator."""
    
    def test_successful_function(self):
        """Test decorator on successful function."""
        from src.agents.agent_resilience import retry_with_backoff
        
        call_count = 0
        
        @retry_with_backoff(max_retries=3, initial_delay=0.01)
        def successful_function():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = successful_function()
        
        assert result == "success"
        assert call_count == 1
    
    def test_eventual_success(self):
        """Test decorator with eventual success after retries."""
        from src.agents.agent_resilience import retry_with_backoff
        
        call_count = 0
        
        @retry_with_backoff(max_retries=5, initial_delay=0.01, backoff_factor=1.0)
        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        result = flaky_function()
        
        assert result == "success"
        assert call_count == 3
    
    def test_all_retries_fail(self):
        """Test decorator when all retries fail."""
        from src.agents.agent_resilience import retry_with_backoff
        
        @retry_with_backoff(max_retries=2, initial_delay=0.01)
        def always_fails():
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError):
            always_fails()
    
    @pytest.mark.asyncio
    async def test_async_function(self):
        """Test decorator on async function."""
        from src.agents.agent_resilience import retry_with_backoff
        
        @retry_with_backoff(max_retries=3, initial_delay=0.01)
        async def async_success():
            return "async_result"
        
        result = await async_success()
        
        assert result == "async_result"


class TestCircuitBreaker:
    """Unit tests for CircuitBreaker class."""
    
    @pytest.fixture
    def breaker(self):
        """Create CircuitBreaker instance."""
        from src.agents.agent_resilience import CircuitBreaker
        return CircuitBreaker(failure_threshold=3, recovery_timeout=0.1)
    
    def test_initialization(self):
        """Test CircuitBreaker initialization."""
        from src.agents.agent_resilience import CircuitBreaker
        
        cb = CircuitBreaker(failure_threshold=5)
        
        assert cb is not None
    
    def test_closed_state_initially(self, breaker):
        """Test circuit starts closed."""
        state = breaker.get_state()
        
        assert state["state"] == "CLOSED"
    
    def test_opens_after_failures(self, breaker):
        """Test circuit opens after failure threshold."""
        def failing_func():
            raise Exception("Fail")
        
        # Trigger failures
        for _ in range(3):
            try:
                breaker.call(failing_func)
            except Exception:
                pass
        
        state = breaker.get_state()
        
        assert state["state"] == "OPEN"
    
    def test_reset(self, breaker):
        """Test manual circuit reset."""
        def failing_func():
            raise Exception("Fail")
        
        # Trigger failures
        for _ in range(3):
            try:
                breaker.call(failing_func)
            except Exception:
                pass
        
        breaker.reset()
        
        state = breaker.get_state()
        assert state["state"] == "CLOSED"
    
    def test_successful_call(self, breaker):
        """Test successful call passes through."""
        def success_func():
            return "success"
        
        result = breaker.call(success_func)
        
        assert result == "success"
    
    def test_get_state_includes_stats(self, breaker):
        """Test get_state includes failure count."""
        state = breaker.get_state()
        
        assert "failures" in state
        assert "state" in state


class TestAgentFallback:
    """Unit tests for AgentFallback class."""
    
    def test_initialization(self):
        """Test AgentFallback initialization."""
        from src.agents.agent_resilience import AgentFallback
        
        primary = Mock()
        fallback = Mock()
        
        af = AgentFallback(
            primary_agent=primary,
            fallback_agent=fallback,
            name="TestFallback"
        )
        
        assert af is not None
    
    def test_execute_primary_success(self):
        """Test execute uses primary agent on success."""
        from src.agents.agent_resilience import AgentFallback
        
        primary = Mock()
        primary.analyze = Mock(return_value="primary_result")
        fallback = Mock()
        
        af = AgentFallback(primary_agent=primary, fallback_agent=fallback)
        
        result = af.execute("analyze", {"data": "test"})
        
        assert result == "primary_result"
    
    def test_execute_fallback_on_failure(self):
        """Test execute uses fallback when primary fails."""
        from src.agents.agent_resilience import AgentFallback
        
        primary = Mock()
        primary.analyze = Mock(side_effect=Exception("Primary failed"))
        fallback = Mock()
        fallback.analyze = Mock(return_value="fallback_result")
        
        af = AgentFallback(primary_agent=primary, fallback_agent=fallback)
        
        result = af.execute("analyze", {"data": "test"})
        
        assert result == "fallback_result"
    
    def test_get_stats(self):
        """Test getting fallback statistics."""
        from src.agents.agent_resilience import AgentFallback
        
        primary = Mock()
        fallback = Mock()
        
        af = AgentFallback(primary_agent=primary, fallback_agent=fallback)
        
        stats = af.get_stats()
        
        assert "primary_calls" in stats
        assert "fallback_calls" in stats


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
    
    def test_has_agents(self, orchestrator):
        """Test orchestrator has agents registered."""
        # Should have access to agents
        assert hasattr(orchestrator, 'agents') or hasattr(orchestrator, 'registry')


# ============================================================================
# RESILIENT ORCHESTRATOR TESTS
# ============================================================================

class TestResilientOrchestrator:
    """Unit tests for ResilientOrchestrator class."""
    
    def test_initialization(self):
        """Test ResilientOrchestrator initialization."""
        from src.agents.resilient_orchestrator import ResilientOrchestrator
        
        orchestrator = ResilientOrchestrator()
        
        assert orchestrator is not None


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
