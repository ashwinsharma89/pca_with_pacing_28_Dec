"""
Intelligent Reporting Module

Provides universal, AI-powered reporting capabilities:
- Multi-source data ingestion (CSV, XLSX, DB, API, JSON, Parquet)
- Intelligent field mapping (pattern + semantic + LLM)
- Automatic template analysis
- Smart data transformation and aggregation
- Universal template population
"""

from .intelligent_reporter import (
    # Main classes
    IntelligentReportSystem,
    IntelligentDataReader,
    FieldMappingEngine,
    DataTransformationEngine,
    TemplateAnalyzer,
    IntelligentTemplateUpdater,
    
    # Data classes
    FieldMapping,
    TemplateStructure,
    DataSourceConfig,
    ReportResult,
    
    # Adapters
    DataSourceAdapter,
    FileAdapter,
    DatabaseAdapter,
    APIAdapter,
    
    # Convenience function
    generate_report,
)

__all__ = [
    'IntelligentReportSystem',
    'IntelligentDataReader',
    'FieldMappingEngine',
    'DataTransformationEngine',
    'TemplateAnalyzer',
    'IntelligentTemplateUpdater',
    'FieldMapping',
    'TemplateStructure',
    'DataSourceConfig',
    'ReportResult',
    'DataSourceAdapter',
    'FileAdapter',
    'DatabaseAdapter',
    'APIAdapter',
    'generate_report',
]
