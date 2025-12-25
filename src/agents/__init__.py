"""AI Agents package."""
from .vision_agent import VisionAgent
from .extraction_agent import ExtractionAgent
from .reasoning_agent import ReasoningAgent
from .visualization_agent import VisualizationAgent
from .report_agent import ReportAgent
from .b2b_specialist_agent import B2BSpecialistAgent
from .enhanced_reasoning_agent import EnhancedReasoningAgent, PatternDetector
from .smart_visualization_engine import SmartVisualizationEngine, VisualizationType, InsightType
from .marketing_visualization_rules import (
    MarketingVisualizationRules,
    MarketingInsightCategory,
    MarketingColorSchemes
)
from .chart_generators import SmartChartGenerator
from .enhanced_visualization_agent import EnhancedVisualizationAgent
from .visualization_filters import SmartFilterEngine, FilterType, FilterCondition
from .filter_presets import FilterPresets

# Prompt Template System for versioned prompt management
from .prompt_templates import (
    PromptTemplate,
    PromptRegistry,
    PromptCategory,
    prompt_registry,
    get_prompt,
    list_prompts
)

__all__ = [
    "VisionAgent",
    "ExtractionAgent",
    "ReasoningAgent",
    "VisualizationAgent",
    "ReportAgent",
    "B2BSpecialistAgent",
    "EnhancedReasoningAgent",
    "PatternDetector",
    "SmartVisualizationEngine",
    "VisualizationType",
    "InsightType",
    "MarketingVisualizationRules",
    "MarketingInsightCategory",
    "MarketingColorSchemes",
    "SmartChartGenerator",
    "EnhancedVisualizationAgent",
    "SmartFilterEngine",
    "FilterType",
    "FilterCondition",
    "FilterPresets",
    # Prompt Templates
    "PromptTemplate",
    "PromptRegistry",
    "PromptCategory",
    "prompt_registry",
    "get_prompt",
    "list_prompts"
]
