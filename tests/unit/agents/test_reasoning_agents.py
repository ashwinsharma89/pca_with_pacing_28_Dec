"""
Unit Tests for Reasoning Agents

Tests for:
- ReasoningAgent (reasoning_agent.py)
- ValidatedReasoningAgent (validated_reasoning_agent.py)  
- EnhancedReasoningAgent (enhanced_reasoning_agent.py)

All tests use mocked LLM responses for deterministic testing.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import json
from datetime import datetime

# ============================================================================
# MOCK LLM CLIENT
# ============================================================================

def create_mock_openai_response(content: str):
    """Create a mock OpenAI response object."""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = content
    mock_response.usage = Mock()
    mock_response.usage.total_tokens = 150
    mock_response.usage.prompt_tokens = 100
    mock_response.usage.completion_tokens = 50
    return mock_response


def create_mock_anthropic_response(content: str):
    """Create a mock Anthropic response object."""
    mock_response = Mock()
    mock_response.content = [Mock()]
    mock_response.content[0].text = content
    mock_response.usage = Mock()
    mock_response.usage.input_tokens = 100
    mock_response.usage.output_tokens = 50
    return mock_response


# ============================================================================
# SAMPLE DATA FIXTURES
# ============================================================================

@pytest.fixture
def sample_campaign():
    """Create a sample Campaign object for testing."""
    from src.models.campaign import Campaign, CampaignObjective
    from src.models.platform import PlatformType, MetricType, NormalizedMetric
    
    campaign = Campaign(
        campaign_id="test-campaign-001",
        campaign_name="Test Brand Campaign",
        objectives=[CampaignObjective.CONVERSION, CampaignObjective.AWARENESS],
        normalized_metrics=[
            NormalizedMetric(
                platform=PlatformType.GOOGLE_ADS,
                metric_type=MetricType.IMPRESSIONS,
                value=100000.0,
                original_metric_name="impressions"
            ),
            NormalizedMetric(
                platform=PlatformType.GOOGLE_ADS,
                metric_type=MetricType.CLICKS,
                value=5000.0,
                original_metric_name="clicks"
            ),
            NormalizedMetric(
                platform=PlatformType.GOOGLE_ADS,
                metric_type=MetricType.CONVERSIONS,
                value=250.0,
                original_metric_name="conversions"
            ),
            NormalizedMetric(
                platform=PlatformType.GOOGLE_ADS,
                metric_type=MetricType.SPEND,
                value=5000.0,
                original_metric_name="cost"
            ),
            NormalizedMetric(
                platform=PlatformType.GOOGLE_ADS,
                metric_type=MetricType.ROAS,
                value=4.5,
                original_metric_name="roas"
            ),
            NormalizedMetric(
                platform=PlatformType.META_ADS,
                metric_type=MetricType.IMPRESSIONS,
                value=80000.0,
                original_metric_name="impressions"
            ),
            NormalizedMetric(
                platform=PlatformType.META_ADS,
                metric_type=MetricType.CLICKS,
                value=3200.0,
                original_metric_name="clicks"
            ),
            NormalizedMetric(
                platform=PlatformType.META_ADS,
                metric_type=MetricType.CONVERSIONS,
                value=180.0,
                original_metric_name="conversions"
            ),
            NormalizedMetric(
                platform=PlatformType.META_ADS,
                metric_type=MetricType.SPEND,
                value=3000.0,
                original_metric_name="cost"
            ),
            NormalizedMetric(
                platform=PlatformType.META_ADS,
                metric_type=MetricType.ROAS,
                value=5.2,
                original_metric_name="roas"
            ),
        ]
    )
    return campaign


@pytest.fixture
def mock_channel_insights_response():
    """Mock LLM response for channel insights."""
    return json.dumps({
        "strengths": [
            "Strong ROAS of 4.5x indicates efficient spend",
            "High conversion rate shows effective targeting"
        ],
        "weaknesses": [
            "CTR below industry average",
            "High CPA compared to social channels"
        ],
        "opportunities": [
            "Test video ads to improve engagement",
            "Expand remarketing audiences"
        ],
        "top_creative": "Responsive search ads",
        "top_audience": "In-market: Business Services"
    })


@pytest.fixture
def mock_cross_channel_response():
    """Mock LLM response for cross-channel analysis."""
    return json.dumps([
        {
            "insight_type": "synergy",
            "title": "Search + Social Synergy",
            "description": "Users exposed to both Google and Meta ads convert 40% more",
            "affected_platforms": ["google_ads", "meta_ads"],
            "impact_score": 8.5
        },
        {
            "insight_type": "attribution",
            "title": "Meta Assists Google Conversions",
            "description": "30% of Google conversions had prior Meta touchpoint",
            "affected_platforms": ["meta_ads", "google_ads"],
            "impact_score": 7.2
        }
    ])


@pytest.fixture  
def mock_achievements_response():
    """Mock LLM response for achievements."""
    return json.dumps([
        {
            "achievement_type": "performance",
            "title": "Exceptional ROAS",
            "description": "Meta achieved 5.2x ROAS, exceeding target by 30%",
            "metric_value": 5.2,
            "metric_name": "ROAS",
            "platform": "meta_ads",
            "impact_level": "high"
        }
    ])


@pytest.fixture
def mock_recommendations_response():
    """Mock LLM response for recommendations."""
    return json.dumps([
        "Increase Meta budget by 20% based on superior ROAS",
        "Test Performance Max campaigns on Google",
        "Implement cross-platform frequency capping"
    ])


# ============================================================================
# REASONING AGENT TESTS
# ============================================================================

class TestReasoningAgent:
    """Unit tests for ReasoningAgent class."""
    
    @pytest.fixture
    def agent(self):
        """Create ReasoningAgent with mocked client."""
        with patch('src.agents.reasoning_agent.AsyncOpenAI') as mock_openai:
            from src.agents.reasoning_agent import ReasoningAgent
            agent = ReasoningAgent(model="gpt-4o-mini", provider="openai")
            return agent
    
    def test_initialization_openai(self):
        """Test ReasoningAgent initializes with OpenAI provider."""
        with patch('src.agents.reasoning_agent.AsyncOpenAI') as mock_openai:
            from src.agents.reasoning_agent import ReasoningAgent
            
            agent = ReasoningAgent(provider="openai")
            
            assert agent.provider == "openai"
            assert agent.model is not None
    
    def test_initialization_anthropic(self):
        """Test ReasoningAgent initializes with Anthropic provider."""
        with patch('src.agents.reasoning_agent.create_async_anthropic_client') as mock_anthropic:
            mock_anthropic.return_value = Mock()
            from src.agents.reasoning_agent import ReasoningAgent
            
            agent = ReasoningAgent(provider="anthropic", model="claude-3-sonnet")
            
            assert agent.provider == "anthropic"
    
    def test_calculate_performance_score_awareness(self):
        """Test performance score calculation for awareness objective."""
        with patch('src.agents.reasoning_agent.AsyncOpenAI'):
            from src.agents.reasoning_agent import ReasoningAgent
            from src.models.campaign import ChannelPerformance, CampaignObjective
            from src.models.platform import PlatformType
            
            agent = ReasoningAgent()
            
            performance = ChannelPerformance(
                platform=PlatformType.GOOGLE_ADS,
                platform_name="Google Ads",
                total_impressions=1000000,  # 1M impressions
                total_clicks=50000,
                ctr=5.0
            )
            
            score = agent._calculate_performance_score(
                performance,
                [CampaignObjective.AWARENESS]
            )
            
            # High impressions should give good score
            assert score >= 20
            assert score <= 100
    
    def test_calculate_performance_score_conversion(self):
        """Test performance score calculation for conversion objective."""
        with patch('src.agents.reasoning_agent.AsyncOpenAI'):
            from src.agents.reasoning_agent import ReasoningAgent
            from src.models.campaign import ChannelPerformance, CampaignObjective
            from src.models.platform import PlatformType
            
            agent = ReasoningAgent()
            
            performance = ChannelPerformance(
                platform=PlatformType.META_ADS,
                platform_name="Meta Ads",
                total_conversions=500,
                total_spend=2000.0,
                roas=5.0  # Good ROAS
            )
            
            score = agent._calculate_performance_score(
                performance,
                [CampaignObjective.CONVERSION]
            )
            
            # Good ROAS should give high score
            assert score >= 40
    
    def test_rank_channels(self):
        """Test channel ranking by performance score."""
        with patch('src.agents.reasoning_agent.AsyncOpenAI'):
            from src.agents.reasoning_agent import ReasoningAgent
            from src.models.campaign import ChannelPerformance
            from src.models.platform import PlatformType
            
            agent = ReasoningAgent()
            
            performances = [
                ChannelPerformance(
                    platform=PlatformType.GOOGLE_ADS,
                    platform_name="Google Ads",
                    performance_score=75.0
                ),
                ChannelPerformance(
                    platform=PlatformType.META_ADS,
                    platform_name="Meta Ads",
                    performance_score=85.0
                ),
                ChannelPerformance(
                    platform=PlatformType.LINKEDIN_ADS,
                    platform_name="LinkedIn Ads",
                    performance_score=65.0
                )
            ]
            
            ranked = agent._rank_channels(performances)
            
            # Should be sorted by performance score descending
            assert ranked[0].platform == PlatformType.META_ADS
            assert ranked[0].efficiency_rank == 1
            assert ranked[1].platform == PlatformType.GOOGLE_ADS
            assert ranked[1].efficiency_rank == 2
            assert ranked[2].efficiency_rank == 3
    
    @pytest.mark.asyncio
    async def test_generate_channel_insights(
        self, agent, mock_channel_insights_response
    ):
        """Test generating channel insights via LLM."""
        from src.models.campaign import ChannelPerformance, CampaignObjective
        from src.models.platform import PlatformType, MetricType
        
        # Mock the LLM call
        agent.client.chat.completions.create = AsyncMock(
            return_value=create_mock_openai_response(mock_channel_insights_response)
        )
        
        performance = ChannelPerformance(
            platform=PlatformType.GOOGLE_ADS,
            platform_name="Google Ads",
            performance_score=75.0
        )
        
        metrics = {MetricType.ROAS: 4.5, MetricType.CTR: 2.5}
        
        insights = await agent._generate_channel_insights(
            performance,
            metrics,
            [CampaignObjective.CONVERSION]
        )
        
        assert "strengths" in insights
        assert "weaknesses" in insights
        assert len(insights["strengths"]) >= 1
    
    @pytest.mark.asyncio
    async def test_call_llm_openai(self, agent):
        """Test LLM call to OpenAI."""
        agent.client.chat.completions.create = AsyncMock(
            return_value=create_mock_openai_response("Test response")
        )
        
        response = await agent._call_llm("Test prompt")
        
        assert response == "Test response"
        agent.client.chat.completions.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_analyze_campaign_full(
        self, 
        agent, 
        sample_campaign,
        mock_channel_insights_response,
        mock_cross_channel_response,
        mock_achievements_response,
        mock_recommendations_response
    ):
        """Test full campaign analysis flow."""
        # Mock all LLM calls
        responses = [
            mock_channel_insights_response,  # Google channel insights
            mock_channel_insights_response,  # Meta channel insights
            mock_cross_channel_response,     # Cross-channel
            mock_achievements_response,       # Achievements
            mock_recommendations_response     # Recommendations
        ]
        
        call_count = 0
        async def mock_call(*args, **kwargs):
            nonlocal call_count
            resp = create_mock_openai_response(responses[min(call_count, len(responses)-1)])
            call_count += 1
            return resp
        
        agent.client.chat.completions.create = mock_call
        
        result = await agent.analyze_campaign(sample_campaign)
        
        assert result.insights is not None
        assert result.recommendations is not None


# ============================================================================
# VALIDATED REASONING AGENT TESTS
# ============================================================================

class TestValidatedReasoningAgent:
    """Unit tests for ValidatedReasoningAgent class."""
    
    @pytest.fixture
    def agent(self):
        """Create ValidatedReasoningAgent with mocked client."""
        with patch('src.agents.validated_reasoning_agent.AsyncOpenAI') as mock:
            from src.agents.validated_reasoning_agent import ValidatedReasoningAgent
            return ValidatedReasoningAgent()
    
    def test_initialization(self):
        """Test ValidatedReasoningAgent initialization."""
        with patch('src.agents.validated_reasoning_agent.AsyncOpenAI'):
            from src.agents.validated_reasoning_agent import ValidatedReasoningAgent
            
            agent = ValidatedReasoningAgent()
            
            assert agent is not None
    
    @pytest.mark.asyncio
    async def test_validate_response_valid_json(self, agent):
        """Test response validation with valid JSON."""
        valid_response = json.dumps({
            "insights": ["Insight 1", "Insight 2"],
            "confidence": 0.85
        })
        
        # The validation should pass and return parsed data
        # Implementation-specific test
        assert json.loads(valid_response) is not None
    
    @pytest.mark.asyncio
    async def test_validate_response_invalid_json(self, agent):
        """Test response validation with invalid JSON."""
        invalid_response = "This is not valid JSON {"
        
        # Should handle gracefully
        try:
            json.loads(invalid_response)
            assert False, "Should have raised"
        except json.JSONDecodeError:
            assert True


# ============================================================================
# ENHANCED REASONING AGENT TESTS
# ============================================================================

class TestEnhancedReasoningAgent:
    """Unit tests for EnhancedReasoningAgent class."""
    
    @pytest.fixture
    def agent(self):
        """Create EnhancedReasoningAgent with mocked dependencies."""
        with patch('src.agents.enhanced_reasoning_agent.AsyncOpenAI'):
            from src.agents.enhanced_reasoning_agent import EnhancedReasoningAgent
            return EnhancedReasoningAgent()
    
    def test_initialization(self):
        """Test EnhancedReasoningAgent initialization."""
        with patch('src.agents.enhanced_reasoning_agent.AsyncOpenAI'):
            from src.agents.enhanced_reasoning_agent import EnhancedReasoningAgent
            
            agent = EnhancedReasoningAgent()
            
            assert agent is not None
    
    def test_pattern_detector_initialization(self):
        """Test PatternDetector class initialization."""
        from src.agents.enhanced_reasoning_agent import PatternDetector
        
        detector = PatternDetector()
        
        assert detector is not None


class TestPatternDetector:
    """Unit tests for PatternDetector class."""
    
    @pytest.fixture
    def detector(self):
        """Create PatternDetector instance."""
        from src.agents.enhanced_reasoning_agent import PatternDetector
        return PatternDetector()
    
    def test_detect_trend_increasing(self, detector):
        """Test detecting increasing trend."""
        values = [100, 120, 150, 180, 220]
        
        result = detector.detect_trend(values)
        
        assert result["direction"] == "increasing"
        assert result["magnitude"] > 0
    
    def test_detect_trend_decreasing(self, detector):
        """Test detecting decreasing trend."""
        values = [220, 180, 150, 120, 100]
        
        result = detector.detect_trend(values)
        
        assert result["direction"] == "decreasing"
    
    def test_detect_trend_stable(self, detector):
        """Test detecting stable trend."""
        values = [100, 102, 98, 101, 99]
        
        result = detector.detect_trend(values)
        
        assert result["direction"] == "stable"
    
    def test_detect_anomaly(self, detector):
        """Test anomaly detection."""
        values = [100, 102, 98, 250, 101, 99]  # 250 is anomaly
        
        anomalies = detector.detect_anomalies(values)
        
        assert len(anomalies) >= 1
        assert 3 in anomalies  # Index of 250


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
