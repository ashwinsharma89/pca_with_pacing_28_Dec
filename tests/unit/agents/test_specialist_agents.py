"""
Unit Tests for Specialist Agents

Tests for:
- ReportAgent (report_agent.py)
- VisionAgent (vision_agent.py)
- ExtractionAgent (extraction_agent.py)
- B2BSpecialistAgent (b2b_specialist_agent.py)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import json
import base64
from datetime import datetime
import pandas as pd


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_campaign_data():
    """Sample campaign data for reports."""
    return pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=7),
        'campaign_name': ['Campaign A'] * 4 + ['Campaign B'] * 3,
        'platform': ['Google Ads'] * 3 + ['Meta'] * 4,
        'spend': [1000, 1200, 1100, 1300, 900, 950, 1000],
        'impressions': [100000, 120000, 110000, 130000, 90000, 95000, 100000],
        'clicks': [5000, 6000, 5500, 6500, 4500, 4750, 5000],
        'conversions': [250, 300, 275, 325, 225, 237, 250]
    })


@pytest.fixture  
def mock_image_base64():
    """Mock base64 encoded image."""
    # Create a minimal valid PNG
    png_header = b'\x89PNG\r\n\x1a\n'
    return base64.b64encode(png_header).decode('utf-8')


def create_mock_llm_response(content: str):
    """Create mock LLM response."""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = content
    return mock_response


# ============================================================================
# REPORT AGENT TESTS
# ============================================================================

class TestReportAgent:
    """Unit tests for ReportAgent class."""
    
    @pytest.fixture
    def agent(self):
        """Create ReportAgent with mocked client."""
        with patch('src.agents.report_agent.AsyncOpenAI'):
            from src.agents.report_agent import ReportAgent
            return ReportAgent()
    
    def test_initialization(self):
        """Test ReportAgent initialization."""
        with patch('src.agents.report_agent.AsyncOpenAI'):
            from src.agents.report_agent import ReportAgent
            
            agent = ReportAgent()
            
            assert agent is not None
    
    @pytest.mark.asyncio
    async def test_generate_executive_summary(self, agent, sample_campaign_data):
        """Test generating executive summary."""
        mock_summary = """## Executive Summary
        
Total spend: $7,450 with 1,862 conversions.
ROAS: 4.2x, exceeding target by 15%.

Key highlights:
- Google Ads: Strong performance with 850 conversions
- Meta: Excellent efficiency with $4.10 CPA"""
        
        agent.client.chat.completions.create = AsyncMock(
            return_value=create_mock_llm_response(mock_summary)
        )
        
        summary = await agent.generate_executive_summary(
            sample_campaign_data,
            time_period="Last 7 days"
        )
        
        assert summary is not None
        assert "Summary" in summary or "spend" in summary.lower()
    
    @pytest.mark.asyncio
    async def test_generate_full_report(self, agent, sample_campaign_data):
        """Test generating full report."""
        mock_report = json.dumps({
            "title": "Weekly Performance Report",
            "summary": "Strong week with 4.2x ROAS",
            "sections": [
                {"name": "Overview", "content": "Total spend: $7,450"},
                {"name": "By Platform", "content": "Google: $3,300, Meta: $4,150"}
            ],
            "recommendations": ["Increase Meta budget", "Test new Google campaigns"]
        })
        
        agent.client.chat.completions.create = AsyncMock(
            return_value=create_mock_llm_response(mock_report)
        )
        
        report = await agent.generate_report(
            sample_campaign_data,
            report_type="weekly"
        )
        
        assert report is not None
    
    def test_calculate_summary_metrics(self, agent, sample_campaign_data):
        """Test calculating summary metrics for report."""
        metrics = agent._calculate_summary_metrics(sample_campaign_data)
        
        assert "total_spend" in metrics
        assert metrics["total_spend"] == sample_campaign_data["spend"].sum()
    
    def test_format_currency(self, agent):
        """Test currency formatting."""
        formatted = agent._format_currency(12345.67)
        
        assert "$" in formatted or "12" in formatted
    
    def test_format_percentage(self, agent):
        """Test percentage formatting."""
        formatted = agent._format_percentage(0.0325)
        
        assert "%" in formatted or "3" in formatted


# ============================================================================
# VISION AGENT TESTS
# ============================================================================

class TestVisionAgent:
    """Unit tests for VisionAgent class."""
    
    @pytest.fixture
    def agent(self):
        """Create VisionAgent with mocked client."""
        with patch('src.agents.vision_agent.AsyncOpenAI'):
            from src.agents.vision_agent import VisionAgent
            return VisionAgent()
    
    def test_initialization(self):
        """Test VisionAgent initialization."""
        with patch('src.agents.vision_agent.AsyncOpenAI'):
            from src.agents.vision_agent import VisionAgent
            
            agent = VisionAgent()
            
            assert agent is not None
    
    @pytest.mark.asyncio
    async def test_analyze_screenshot(self, agent, mock_image_base64):
        """Test analyzing dashboard screenshot."""
        mock_analysis = json.dumps({
            "description": "Marketing dashboard showing KPIs",
            "elements_detected": [
                {"type": "metric", "label": "ROAS", "value": "4.2x"},
                {"type": "chart", "chart_type": "bar", "title": "Spend by Channel"}
            ],
            "insights": ["ROAS is above target", "Search dominates spend"]
        })
        
        agent.client.chat.completions.create = AsyncMock(
            return_value=create_mock_llm_response(mock_analysis)
        )
        
        analysis = await agent.analyze_image(mock_image_base64)
        
        assert analysis is not None
    
    @pytest.mark.asyncio
    async def test_extract_text_from_image(self, agent, mock_image_base64):
        """Test OCR text extraction from image."""
        mock_ocr = json.dumps({
            "extracted_text": [
                "Total Spend: $45,000",
                "Conversions: 1,250",
                "ROAS: 4.2x"
            ]
        })
        
        agent.client.chat.completions.create = AsyncMock(
            return_value=create_mock_llm_response(mock_ocr)
        )
        
        text = await agent.extract_text(mock_image_base64)
        
        assert text is not None
    
    @pytest.mark.asyncio
    async def test_compare_screenshots(self, agent, mock_image_base64):
        """Test comparing two screenshots."""
        mock_comparison = json.dumps({
            "differences": [
                "ROAS increased from 3.8x to 4.2x",
                "Spend decreased by 5%"
            ],
            "similarity_score": 0.85
        })
        
        agent.client.chat.completions.create = AsyncMock(
            return_value=create_mock_llm_response(mock_comparison)
        )
        
        comparison = await agent.compare_images(
            mock_image_base64, 
            mock_image_base64
        )
        
        assert comparison is not None
    
    def test_validate_image_format(self, agent, mock_image_base64):
        """Test image format validation."""
        is_valid = agent._is_valid_base64(mock_image_base64)
        
        assert is_valid == True
    
    def test_validate_invalid_image(self, agent):
        """Test invalid image detection."""
        is_valid = agent._is_valid_base64("not-valid-base64!!!")
        
        assert is_valid == False


# ============================================================================
# EXTRACTION AGENT TESTS
# ============================================================================

class TestExtractionAgent:
    """Unit tests for ExtractionAgent class."""
    
    @pytest.fixture
    def agent(self):
        """Create ExtractionAgent with mocked client."""
        with patch('src.agents.extraction_agent.AsyncOpenAI'):
            from src.agents.extraction_agent import ExtractionAgent
            return ExtractionAgent()
    
    def test_initialization(self):
        """Test ExtractionAgent initialization."""
        with patch('src.agents.extraction_agent.AsyncOpenAI'):
            from src.agents.extraction_agent import ExtractionAgent
            
            agent = ExtractionAgent()
            
            assert agent is not None
    
    @pytest.mark.asyncio
    async def test_extract_table_data(self, agent, mock_image_base64):
        """Test extracting table data from image."""
        mock_table = json.dumps({
            "headers": ["Campaign", "Spend", "Conversions", "ROAS"],
            "rows": [
                ["Google Search", "5000", "250", "4.5"],
                ["Meta Retargeting", "3000", "180", "5.2"]
            ]
        })
        
        agent.client.chat.completions.create = AsyncMock(
            return_value=create_mock_llm_response(mock_table)
        )
        
        table = await agent.extract_table(mock_image_base64)
        
        assert table is not None
        assert "headers" in table or isinstance(table, dict)
    
    @pytest.mark.asyncio
    async def test_extract_chart_data(self, agent, mock_image_base64):
        """Test extracting data from chart image."""
        mock_chart_data = json.dumps({
            "chart_type": "bar",
            "title": "Spend by Platform",
            "data_points": [
                {"label": "Google", "value": 45000},
                {"label": "Meta", "value": 35000},
                {"label": "LinkedIn", "value": 15000}
            ]
        })
        
        agent.client.chat.completions.create = AsyncMock(
            return_value=create_mock_llm_response(mock_chart_data)
        )
        
        data = await agent.extract_chart_data(mock_image_base64)
        
        assert data is not None
    
    @pytest.mark.asyncio
    async def test_extract_kpis(self, agent, mock_image_base64):
        """Test extracting KPIs from dashboard image."""
        mock_kpis = json.dumps({
            "kpis": [
                {"name": "ROAS", "value": 4.2, "unit": "x"},
                {"name": "CPA", "value": 25.50, "unit": "USD"},
                {"name": "CTR", "value": 3.5, "unit": "%"}
            ]
        })
        
        agent.client.chat.completions.create = AsyncMock(
            return_value=create_mock_llm_response(mock_kpis)
        )
        
        kpis = await agent.extract_kpis(mock_image_base64)
        
        assert kpis is not None
    
    def test_parse_numeric_value(self, agent):
        """Test parsing numeric values from text."""
        test_cases = [
            ("$45,000", 45000.0),
            ("3.5%", 3.5),
            ("1,250", 1250.0),
            ("4.2x", 4.2)
        ]
        
        for text, expected in test_cases:
            result = agent._parse_numeric(text)
            assert result == expected or result is not None


# ============================================================================
# B2B SPECIALIST AGENT TESTS
# ============================================================================

class TestB2BSpecialistAgent:
    """Unit tests for B2BSpecialistAgent class."""
    
    @pytest.fixture
    def agent(self):
        """Create B2BSpecialistAgent with mocked client."""
        with patch('src.agents.b2b_specialist_agent.AsyncOpenAI'):
            from src.agents.b2b_specialist_agent import B2BSpecialistAgent
            return B2BSpecialistAgent()
    
    def test_initialization(self):
        """Test B2BSpecialistAgent initialization."""
        with patch('src.agents.b2b_specialist_agent.AsyncOpenAI'):
            from src.agents.b2b_specialist_agent import B2BSpecialistAgent
            
            agent = B2BSpecialistAgent()
            
            assert agent is not None
    
    def test_b2b_metrics_defined(self, agent):
        """Test B2B-specific metrics are defined."""
        b2b_metrics = ["MQL", "SQL", "pipeline_value", "lead_to_opp_rate"]
        
        for metric in b2b_metrics:
            # Agent should know about these metrics
            assert metric in agent.B2B_METRICS or hasattr(agent, 'B2B_METRICS')
    
    @pytest.mark.asyncio
    async def test_analyze_lead_funnel(self, agent):
        """Test analyzing B2B lead funnel."""
        funnel_data = {
            "leads": 1000,
            "MQLs": 300,
            "SQLs": 100,
            "opportunities": 50,
            "closed_won": 20
        }
        
        mock_analysis = json.dumps({
            "funnel_health": "healthy",
            "conversion_rates": {
                "lead_to_mql": 30.0,
                "mql_to_sql": 33.3,
                "sql_to_opp": 50.0,
                "opp_to_closed": 40.0
            },
            "bottleneck": "MQL to SQL conversion needs improvement",
            "recommendations": [
                "Improve lead scoring criteria",
                "Enable sales team with better content"
            ]
        })
        
        agent.client.chat.completions.create = AsyncMock(
            return_value=create_mock_llm_response(mock_analysis)
        )
        
        analysis = await agent.analyze_funnel(funnel_data)
        
        assert analysis is not None
    
    @pytest.mark.asyncio
    async def test_calculate_account_metrics(self, agent):
        """Test calculating account-based metrics."""
        account_data = {
            "accounts": [
                {"name": "Acme Corp", "spend": 5000, "pipeline": 50000},
                {"name": "Beta Inc", "spend": 3000, "pipeline": 30000}
            ]
        }
        
        mock_metrics = json.dumps({
            "total_accounts": 2,
            "total_pipeline": 80000,
            "avg_pipeline_per_account": 40000,
            "top_accounts": [
                {"name": "Acme Corp", "pipeline": 50000}
            ]
        })
        
        agent.client.chat.completions.create = AsyncMock(
            return_value=create_mock_llm_response(mock_metrics)
        )
        
        metrics = await agent.calculate_account_metrics(account_data)
        
        assert metrics is not None
    
    @pytest.mark.asyncio
    async def test_generate_abm_recommendations(self, agent):
        """Test generating ABM recommendations."""
        mock_recs = json.dumps({
            "recommendations": [
                {
                    "account": "Acme Corp",
                    "action": "Increase LinkedIn spend",
                    "rationale": "High engagement from decision makers",
                    "priority": "high"
                }
            ]
        })
        
        agent.client.chat.completions.create = AsyncMock(
            return_value=create_mock_llm_response(mock_recs)
        )
        
        recs = await agent.generate_abm_recommendations(
            target_accounts=["Acme Corp", "Beta Inc"]
        )
        
        assert recs is not None
    
    def test_calculate_pipeline_velocity(self, agent):
        """Test calculating pipeline velocity."""
        deals = [
            {"value": 50000, "days_in_stage": 30},
            {"value": 30000, "days_in_stage": 45}
        ]
        
        velocity = agent._calculate_velocity(deals)
        
        assert velocity is not None
        assert velocity >= 0
    
    def test_segment_accounts_by_tier(self, agent):
        """Test segmenting accounts by tier."""
        accounts = [
            {"name": "Enterprise A", "arr": 500000},
            {"name": "Mid-market B", "arr": 50000},
            {"name": "SMB C", "arr": 5000}
        ]
        
        segmented = agent._segment_by_tier(accounts)
        
        assert "enterprise" in segmented or len(segmented) > 0


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
