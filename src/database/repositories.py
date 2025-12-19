"""
Repository pattern for data access.
Provides clean abstraction over database operations.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from src.database.models import Campaign, Analysis, QueryHistory, LLMUsage, CampaignContext

logger = logging.getLogger(__name__)


class BaseRepository:
    """Base repository with common operations."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def commit(self):
        """Commit transaction."""
        self.session.commit()
    
    def rollback(self):
        """Rollback transaction."""
        self.session.rollback()
    
    def flush(self):
        """Flush changes to database."""
        self.session.flush()


class CampaignRepository(BaseRepository):
    """Repository for Campaign operations."""
    
    def create(self, campaign_data: Dict[str, Any]) -> Campaign:
        """Create a new campaign."""
        campaign = Campaign(**campaign_data)
        self.session.add(campaign)
        self.session.flush()
        return campaign
    
    def create_bulk(self, campaigns_data: List[Dict[str, Any]]) -> List[Campaign]:
        """Create multiple campaigns."""
        campaigns = [Campaign(**data) for data in campaigns_data]
        self.session.bulk_save_objects(campaigns, return_defaults=True)
        self.session.flush()
        return campaigns
    
    def get_by_id(self, campaign_id: int) -> Optional[Campaign]:
        """Get campaign by ID."""
        return self.session.query(Campaign).filter(Campaign.id == campaign_id).first()
    
    def get_by_campaign_id(self, campaign_id: str) -> Optional[Campaign]:
        """Get campaign by campaign_id string."""
        return self.session.query(Campaign).filter(Campaign.campaign_id == campaign_id).first()
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[Campaign]:
        """Get all campaigns with pagination."""
        return self.session.query(Campaign).offset(offset).limit(limit).all()
    
    def count_all(self) -> int:
        """Count total campaigns."""
        return self.session.query(Campaign).count()
    
    def get_by_platform(self, platform: str, limit: int = 100) -> List[Campaign]:
        """Get campaigns by platform (case-insensitive)."""
        return self.session.query(Campaign).filter(
            Campaign.platform.ilike(platform)
        ).limit(limit).all()
    
    def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Campaign]:
        """Get campaigns within date range."""
        return self.session.query(Campaign).filter(
            and_(
                Campaign.date >= start_date,
                Campaign.date <= end_date
            )
        ).all()
    
    def search(self, filters: Dict[str, Any], limit: int = 100) -> List[Campaign]:
        """Search campaigns with filters."""
        query = self.session.query(Campaign)
        
        if 'platform' in filters:
            query = query.filter(Campaign.platform.ilike(filters['platform']))
        
        if 'channel' in filters:
            query = query.filter(Campaign.channel.ilike(filters['channel']))
        
        if 'funnel_stage' in filters:
            query = query.filter(Campaign.funnel_stage == filters['funnel_stage'])
        
        if 'start_date' in filters and 'end_date' in filters:
            query = query.filter(
                and_(
                    Campaign.date >= filters['start_date'],
                    Campaign.date <= filters['end_date']
                )
            )
        
        if 'min_spend' in filters:
            query = query.filter(Campaign.spend >= filters['min_spend'])
        
        if 'min_conversions' in filters:
            query = query.filter(Campaign.conversions >= filters['min_conversions'])
        
        return query.limit(limit).all()
    
    def update(self, campaign_id: int, update_data: Dict[str, Any]) -> Optional[Campaign]:
        """Update campaign."""
        campaign = self.get_by_id(campaign_id)
        if campaign:
            for key, value in update_data.items():
                if hasattr(campaign, key):
                    setattr(campaign, key, value)
            self.session.flush()
        return campaign
    
    def delete(self, campaign_id: int) -> bool:
        """Delete campaign."""
        campaign = self.get_by_id(campaign_id)
        if campaign:
            self.session.delete(campaign)
            self.session.flush()
            return True
        return False

    def delete_all(self) -> int:
        """Delete all campaigns (clear cache)."""
        result = self.session.query(Campaign).delete()
        self.session.flush()
        return result
    
    def get_aggregated_metrics(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get aggregated metrics across campaigns."""
        from sqlalchemy import func
        
        query = self.session.query(
            func.sum(Campaign.spend).label('total_spend'),
            func.sum(Campaign.impressions).label('total_impressions'),
            func.sum(Campaign.clicks).label('total_clicks'),
            func.sum(Campaign.conversions).label('total_conversions'),
            func.count(Campaign.id).label('campaign_count')
        )
        
        if filters:
            if 'platform' in filters:
                query = query.filter(Campaign.platform.ilike(filters['platform']))
            if 'start_date' in filters and 'end_date' in filters:
                query = query.filter(
                    and_(
                        Campaign.date >= filters['start_date'],
                        Campaign.date <= filters['end_date']
                    )
                )
        
        result = query.first()
        
        # Calculate derived metrics from aggregates (not averaging individual values)
        total_spend = float(result.total_spend or 0)
        total_impressions = int(result.total_impressions or 0)
        total_clicks = int(result.total_clicks or 0)
        total_conversions = int(result.total_conversions or 0)
        
        avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        avg_cpc = (total_spend / total_clicks) if total_clicks > 0 else 0
        avg_cpa = (total_spend / total_conversions) if total_conversions > 0 else 0
        
        return {
            'total_spend': total_spend,
            'total_impressions': total_impressions,
            'total_clicks': total_clicks,
            'total_conversions': total_conversions,
            'avg_ctr': avg_ctr,
            'avg_cpc': avg_cpc,
            'avg_cpa': avg_cpa,
            'campaign_count': int(result.campaign_count or 0)
        }

    def get_grouped_metrics(self, x_axis: str, y_metrics: List[str], filters: Optional[Dict[str, Any]] = None, aggregation: str = "sum") -> List[Dict[str, Any]]:
        """Get metrics grouped by a dimension using server-side aggregation."""
        from sqlalchemy import func
        
        # Validate that the requested columns exist in the model
        if not hasattr(Campaign, x_axis):
            logger.warning(f"Column {x_axis} not found in Campaign model")
            return []
            
        # Build aggregation functions
        agg_map = {
            'sum': func.sum,
            'avg': func.avg,
            'count': func.count,
            'max': func.max,
            'min': func.min
        }
        agg_func = agg_map.get(aggregation, func.sum)
        
        # Build query
        group_attr = getattr(Campaign, x_axis)
        select_cols = [group_attr.label(x_axis)]
        
        for metric in y_metrics:
            if hasattr(Campaign, metric):
                select_cols.append(agg_func(getattr(Campaign, metric)).label(metric))
            else:
                logger.warning(f"Metric column {metric} not found in Campaign model")
        
        query = self.session.query(*select_cols).group_by(group_attr)
        
        # Apply filters
        if filters:
            if 'platforms' in filters and filters['platforms']:
                query = query.filter(Campaign.platform.in_(filters['platforms']))
            if 'start_date' in filters and 'end_date' in filters:
                query = query.filter(
                    and_(
                        Campaign.date >= filters['start_date'],
                        Campaign.date <= filters['end_date']
                    )
                )
        
        results = query.all()
        return [dict(r._mapping) for r in results]


class AnalysisRepository(BaseRepository):
    """Repository for Analysis operations."""
    
    def create(self, analysis_data: Dict[str, Any]) -> Analysis:
        """Create a new analysis."""
        analysis = Analysis(**analysis_data)
        self.session.add(analysis)
        self.session.flush()
        return analysis
    
    def get_by_id(self, analysis_id: int) -> Optional[Analysis]:
        """Get analysis by ID."""
        return self.session.query(Analysis).filter(Analysis.id == analysis_id).first()
    
    def get_by_analysis_id(self, analysis_id: str) -> Optional[Analysis]:
        """Get analysis by analysis_id string."""
        return self.session.query(Analysis).filter(Analysis.analysis_id == analysis_id).first()
    
    def get_by_campaign(self, campaign_id: int, limit: int = 10) -> List[Analysis]:
        """Get analyses for a campaign."""
        return self.session.query(Analysis).filter(
            Analysis.campaign_id == campaign_id
        ).order_by(desc(Analysis.created_at)).limit(limit).all()
    
    def get_by_type(self, analysis_type: str, limit: int = 100) -> List[Analysis]:
        """Get analyses by type."""
        return self.session.query(Analysis).filter(
            Analysis.analysis_type == analysis_type
        ).order_by(desc(Analysis.created_at)).limit(limit).all()
    
    def get_recent(self, limit: int = 10) -> List[Analysis]:
        """Get recent analyses."""
        return self.session.query(Analysis).order_by(
            desc(Analysis.created_at)
        ).limit(limit).all()
    
    def update_status(self, analysis_id: int, status: str, error_message: Optional[str] = None) -> Optional[Analysis]:
        """Update analysis status."""
        analysis = self.get_by_id(analysis_id)
        if analysis:
            analysis.status = status
            if error_message:
                analysis.error_message = error_message
            if status == 'completed':
                analysis.completed_at = datetime.utcnow()
            self.session.flush()
        return analysis
    
    def update_results(self, analysis_id: int, results: Dict[str, Any]) -> Optional[Analysis]:
        """Update analysis results."""
        analysis = self.get_by_id(analysis_id)
        if analysis:
            if 'insights' in results:
                analysis.insights = results['insights']
            if 'recommendations' in results:
                analysis.recommendations = results['recommendations']
            if 'metrics' in results:
                analysis.metrics = results['metrics']
            if 'executive_summary' in results:
                analysis.executive_summary = results['executive_summary']
            if 'execution_time' in results:
                analysis.execution_time = results['execution_time']
            self.session.flush()
        return analysis


class QueryHistoryRepository(BaseRepository):
    """Repository for QueryHistory operations."""
    
    def create(self, query_data: Dict[str, Any]) -> QueryHistory:
        """Create a new query history entry."""
        query = QueryHistory(**query_data)
        self.session.add(query)
        self.session.flush()
        return query
    
    def get_by_id(self, query_id: int) -> Optional[QueryHistory]:
        """Get query by ID."""
        return self.session.query(QueryHistory).filter(QueryHistory.id == query_id).first()
    
    def get_recent(self, limit: int = 50) -> List[QueryHistory]:
        """Get recent queries."""
        return self.session.query(QueryHistory).order_by(
            desc(QueryHistory.created_at)
        ).limit(limit).all()
    
    def search_by_text(self, search_text: str, limit: int = 20) -> List[QueryHistory]:
        """Search queries by text."""
        return self.session.query(QueryHistory).filter(
            QueryHistory.user_query.ilike(f'%{search_text}%')
        ).order_by(desc(QueryHistory.created_at)).limit(limit).all()
    
    def get_by_status(self, status: str, limit: int = 100) -> List[QueryHistory]:
        """Get queries by status."""
        return self.session.query(QueryHistory).filter(
            QueryHistory.status == status
        ).order_by(desc(QueryHistory.created_at)).limit(limit).all()


class LLMUsageRepository(BaseRepository):
    """Repository for LLM usage tracking."""
    
    def create(self, usage_data: Dict[str, Any]) -> LLMUsage:
        """Create a new LLM usage entry."""
        usage = LLMUsage(**usage_data)
        self.session.add(usage)
        self.session.flush()
        return usage
    
    def get_usage_by_provider(self, provider: str, start_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get aggregated usage by provider."""
        from sqlalchemy import func
        
        query = self.session.query(
            func.sum(LLMUsage.total_tokens).label('total_tokens'),
            func.sum(LLMUsage.cost).label('total_cost'),
            func.count(LLMUsage.id).label('request_count')
        ).filter(LLMUsage.provider == provider)
        
        if start_date:
            query = query.filter(LLMUsage.created_at >= start_date)
        
        result = query.first()
        
        return {
            'provider': provider,
            'total_tokens': int(result.total_tokens or 0),
            'total_cost': float(result.total_cost or 0),
            'request_count': int(result.request_count or 0)
        }
    
    def get_usage_by_operation(self, operation: str, start_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get aggregated usage by operation."""
        from sqlalchemy import func
        
        query = self.session.query(
            func.sum(LLMUsage.total_tokens).label('total_tokens'),
            func.sum(LLMUsage.cost).label('total_cost'),
            func.count(LLMUsage.id).label('request_count')
        ).filter(LLMUsage.operation == operation)
        
        if start_date:
            query = query.filter(LLMUsage.created_at >= start_date)
        
        result = query.first()
        
        return {
            'operation': operation,
            'total_tokens': int(result.total_tokens or 0),
            'total_cost': float(result.total_cost or 0),
            'request_count': int(result.request_count or 0)
        }
    
    def get_total_usage(self, start_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get total usage across all providers."""
        from sqlalchemy import func
        
        query = self.session.query(
            func.sum(LLMUsage.total_tokens).label('total_tokens'),
            func.sum(LLMUsage.cost).label('total_cost'),
            func.count(LLMUsage.id).label('request_count')
        )
        
        if start_date:
            query = query.filter(LLMUsage.created_at >= start_date)
        
        result = query.first()
        
        return {
            'total_tokens': int(result.total_tokens or 0),
            'total_cost': float(result.total_cost or 0),
            'request_count': int(result.request_count or 0)
        }


class CampaignContextRepository(BaseRepository):
    """Repository for CampaignContext operations."""
    
    def create(self, context_data: Dict[str, Any]) -> CampaignContext:
        """Create campaign context."""
        context = CampaignContext(**context_data)
        self.session.add(context)
        self.session.flush()
        return context
    
    def get_by_campaign_id(self, campaign_id: int) -> Optional[CampaignContext]:
        """Get context for a campaign."""
        return self.session.query(CampaignContext).filter(
            CampaignContext.campaign_id == campaign_id
        ).first()
    
    def update(self, campaign_id: int, update_data: Dict[str, Any]) -> Optional[CampaignContext]:
        """Update campaign context."""
        context = self.get_by_campaign_id(campaign_id)
        if context:
            for key, value in update_data.items():
                if hasattr(context, key):
                    setattr(context, key, value)
            self.session.flush()
        else:
            # Create if doesn't exist
            update_data['campaign_id'] = campaign_id
            context = self.create(update_data)
        return context
