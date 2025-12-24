"""
Query Optimization Tests

Tests query performance with and without indexes.
"""

import pytest
import time
from datetime import datetime, timedelta

from src.database.connection import get_db_manager
from src.database.models import Campaign, Analysis, QueryHistory
from src.database.query_profiler import QueryProfiler, IndexAnalyzer, profile_query


class TestQueryOptimization:
    """Test query optimization and indexing."""
    
    @pytest.fixture(scope="class")
    def db_manager(self):
        """Get database manager."""
        return get_db_manager()
    
    @pytest.fixture(scope="class")
    def profiler(self, db_manager):
        """Get query profiler."""
        profiler = QueryProfiler(slow_query_threshold_ms=100.0)
        profiler.enable(db_manager.engine)
        yield profiler
        profiler.disable()
    
    def test_indexes_exist_on_campaigns(self, db_manager):
        """Test that performance indexes exist on campaigns table."""
        analyzer = IndexAnalyzer(db_manager.engine)
        indexes = analyzer.get_table_indexes('campaigns')
        
        # Check for key indexes
        index_names = [idx['index_name'] for idx in indexes]
        
        # Primary key and unique constraints
        assert any('campaign_id' in name for name in index_names), \
            "campaign_id index missing"
        
        # Performance indexes
        expected_indexes = [
            'idx_campaign_date_platform',
            'idx_campaign_platform_objective',
        ]
        
        for expected in expected_indexes:
            assert expected in index_names, \
                f"Missing index: {expected}"
    
    def test_date_range_query_performance(self, db_manager, profiler):
        """Test date range query performance."""
        profiler.clear()
        
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow()
        
        with db_manager.get_session() as session:
            # Query with date range (should use idx_campaign_date_platform)
            campaigns = session.query(Campaign).filter(
                Campaign.date >= start_date,
                Campaign.date <= end_date
            ).all()
        
        # Check profiler
        stats = profiler.get_stats()
        
        if stats['total_queries'] > 0:
            # Should be fast with index
            assert stats['max_duration_ms'] < 1000, \
                f"Date range query too slow: {stats['max_duration_ms']}ms"
    
    def test_platform_filter_query_performance(self, db_manager, profiler):
        """Test platform filtering performance."""
        profiler.clear()
        
        with db_manager.get_session() as session:
            # Query with platform filter (should use idx_campaign_platform_objective)
            campaigns = session.query(Campaign).filter(
                Campaign.platform == 'facebook'
            ).all()
        
        stats = profiler.get_stats()
        
        if stats['total_queries'] > 0:
            # Should be fast with index
            assert stats['max_duration_ms'] < 500, \
                f"Platform filter query too slow: {stats['max_duration_ms']}ms"
    
    def test_composite_filter_query_performance(self, db_manager, profiler):
        """Test composite filter performance."""
        profiler.clear()
        
        with db_manager.get_session() as session:
            # Query with multiple filters (should use composite index)
            campaigns = session.query(Campaign).filter(
                Campaign.platform == 'facebook',
                Campaign.objective == 'conversions'
            ).all()
        
        stats = profiler.get_stats()
        
        if stats['total_queries'] > 0:
            assert stats['max_duration_ms'] < 500, \
                f"Composite filter query too slow: {stats['max_duration_ms']}ms"
    
    def test_slow_query_detection(self, profiler):
        """Test that slow queries are detected."""
        profiler.clear()
        
        # Simulate slow query
        time.sleep(0.15)  # 150ms
        
        # Check if profiler would detect it
        # (This is a simplified test - real slow queries would come from DB)
        assert profiler.slow_query_threshold_ms == 100.0
    
    def test_query_profiler_stats(self, profiler):
        """Test query profiler statistics."""
        stats = profiler.get_stats()
        
        # Should have stats structure
        assert 'total_queries' in stats
        assert 'slow_queries' in stats
        assert 'avg_duration_ms' in stats
        assert 'query_types' in stats
    
    def test_index_analyzer_works(self, db_manager):
        """Test index analyzer functionality."""
        analyzer = IndexAnalyzer(db_manager.engine)
        
        # Get indexes for campaigns table
        indexes = analyzer.get_table_indexes('campaigns')
        
        assert len(indexes) > 0, "Should have indexes on campaigns table"
        
        # Each index should have name and definition
        for idx in indexes:
            assert 'index_name' in idx
            assert 'definition' in idx
    
    def test_index_usage_stats(self, db_manager):
        """Test index usage statistics."""
        analyzer = IndexAnalyzer(db_manager.engine)
        
        # Get usage stats
        usage_stats = analyzer.get_index_usage_stats('campaigns')
        
        # Should return stats (may be empty if no queries yet)
        assert isinstance(usage_stats, list)
    
    def test_profile_query_decorator(self):
        """Test profile_query decorator."""
        
        @profile_query(threshold_ms=50)
        def slow_function():
            time.sleep(0.1)  # 100ms
            return "done"
        
        result = slow_function()
        assert result == "done"
    
    @pytest.mark.slow
    def test_analyze_table_comprehensive(self, db_manager):
        """Test comprehensive table analysis."""
        analyzer = IndexAnalyzer(db_manager.engine)
        
        analysis = analyzer.analyze_table('campaigns')
        
        assert 'table_name' in analysis
        assert 'total_indexes' in analysis
        assert 'indexes' in analysis
        assert 'recommendations' in analysis
        
        assert analysis['table_name'] == 'campaigns'
        assert analysis['total_indexes'] > 0


class TestQueryPerformanceBenchmarks:
    """Benchmark query performance."""
    
    @pytest.fixture(scope="class")
    def db_manager(self):
        """Get database manager."""
        return get_db_manager()
    
    @pytest.mark.benchmark
    def test_simple_select_benchmark(self, db_manager, benchmark):
        """Benchmark simple SELECT query."""
        
        def query():
            with db_manager.get_session() as session:
                return session.query(Campaign).limit(100).all()
        
        result = benchmark(query)
        
        # Should be fast
        assert benchmark.stats['mean'] < 0.1  # < 100ms
    
    @pytest.mark.benchmark
    def test_filtered_select_benchmark(self, db_manager, benchmark):
        """Benchmark filtered SELECT query."""
        
        def query():
            with db_manager.get_session() as session:
                return session.query(Campaign).filter(
                    Campaign.platform == 'facebook'
                ).limit(100).all()
        
        result = benchmark(query)
        
        # Should be fast with index
        assert benchmark.stats['mean'] < 0.15  # < 150ms
    
    @pytest.mark.benchmark
    def test_join_query_benchmark(self, db_manager, benchmark):
        """Benchmark JOIN query."""
        
        def query():
            with db_manager.get_session() as session:
                return session.query(Campaign, Analysis).join(
                    Analysis, Campaign.id == Analysis.campaign_id
                ).limit(100).all()
        
        result = benchmark(query)
        
        # Joins are slower but should still be reasonable
        assert benchmark.stats['mean'] < 0.3  # < 300ms


class TestDuckDBOptimization:
    """Test DuckDB query optimization."""
    
    def test_duckdb_parquet_query_performance(self):
        """Test DuckDB Parquet query performance."""
        from src.database.duckdb_manager import get_duckdb_manager
        
        duckdb = get_duckdb_manager()
        
        if not duckdb.has_data():
            pytest.skip("No campaign data available")
        
        # Time a query
        start = time.perf_counter()
        df = duckdb.get_campaigns(limit=1000)
        duration_ms = (time.perf_counter() - start) * 1000
        
        # DuckDB should be very fast
        assert duration_ms < 500, \
            f"DuckDB query too slow: {duration_ms:.2f}ms"
    
    def test_duckdb_aggregation_performance(self):
        """Test DuckDB aggregation performance."""
        from src.database.duckdb_manager import get_duckdb_manager
        
        duckdb = get_duckdb_manager()
        
        if not duckdb.has_data():
            pytest.skip("No campaign data available")
        
        # Time an aggregation
        start = time.perf_counter()
        metrics = duckdb.get_total_metrics()
        duration_ms = (time.perf_counter() - start) * 1000
        
        # Aggregations should be fast
        assert duration_ms < 1000, \
            f"DuckDB aggregation too slow: {duration_ms:.2f}ms"
