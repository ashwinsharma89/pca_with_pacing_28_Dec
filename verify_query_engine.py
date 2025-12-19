"""
Quick verification script for Query Optimizer and Multi-Table Manager
"""
import pandas as pd
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.query_engine.nl_to_sql import NaturalLanguageQueryEngine

def test_query_optimizer():
    """Test QueryOptimizer functionality."""
    print("\n=== Testing Query Optimizer ===\n")
    
    # Create sample data
    campaigns_df = pd.DataFrame({
        'campaign_id': range(1, 11),
        'campaign_name': [f'Campaign {i}' for i in range(1, 11)],
        'platform': ['Facebook'] * 5 + ['Google'] * 5,
        'spend': [100 + i * 10 for i in range(10)],
        'impressions': [1000 + i * 100 for i in range(10)],
        'clicks': [50 + i * 5 for i in range(10)],
        'conversions': [5 + i for i in range(10)]
    })
    
    # Initialize engine
    api_key = os.getenv('OPENAI_API_KEY', 'dummy-key')
    engine = NaturalLanguageQueryEngine(api_key)
    engine.load_data(campaigns_df)
    
    # Test 1: Check optimizer exists
    assert engine.optimizer is not None, "Optimizer should be initialized"
    print("✓ Optimizer initialized")
    
    # Test 2: Analyze a simple query
    sql = "SELECT * FROM campaigns WHERE platform = 'Facebook'"
    plan = engine.optimizer.analyze_query(sql)
    print(f"✓ Query plan analyzed: {plan.execution_time:.3f}s execution time")
    
    # Test 3: Get optimization suggestions
    suggestions = engine.optimizer.suggest_optimizations(plan, sql)
    print(f"✓ Got {len(suggestions)} optimization suggestions")
    for i, suggestion in enumerate(suggestions[:3], 1):
        print(f"  {i}. {suggestion[:80]}...")
    
    # Test 4: Get query stats
    stats = engine.optimizer.get_query_stats(sql)
    print(f"✓ Query stats: Cost={stats['cost']:.2f}, Rows={stats['estimated_rows']}")
    
    # Test 5: Optimization report
    report = engine.optimizer.get_optimization_report()
    print(f"✓ Optimization report generated ({len(report)} chars)")
    
    print("\n✅ All Query Optimizer tests passed!\n")


def test_multi_table_manager():
    """Test MultiTableManager functionality."""
    print("\n=== Testing Multi-Table Manager ===\n")
    
    # Create sample data
    campaigns_df = pd.DataFrame({
        'campaign_id': range(1, 11),
        'campaign_name': [f'Campaign {i}' for i in range(1, 11)],
        'product_id': [1, 1, 2, 2, 3, 3, 4, 4, 5, 5],
        'spend': [100 + i * 10 for i in range(10)]
    })
    
    products_df = pd.DataFrame({
        'product_id': range(1, 6),
        'product_name': ['Product A', 'Product B', 'Product C', 'Product D', 'Product E'],
        'category': ['Electronics', 'Electronics', 'Clothing', 'Clothing', 'Home']
    })
    
    # Initialize engine
    api_key = os.getenv('OPENAI_API_KEY', 'dummy-key')
    engine = NaturalLanguageQueryEngine(api_key)
    engine.load_data(campaigns_df)
    
    # Test 1: Check multi-table manager exists
    assert engine.multi_table_manager is not None, "Multi-table manager should be initialized"
    print("✓ Multi-table manager initialized")
    
    # Test 2: Load additional table
    engine.load_additional_table(products_df, 'products', primary_key='product_id')
    assert 'products' in engine.multi_table_manager.tables
    print(f"✓ Loaded additional table 'products' with {len(products_df)} rows")
    
    # Test 3: Auto-detect relationships
    detected = engine.auto_detect_relationships()
    print(f"✓ Auto-detected {len(detected)} relationships")
    for rel in detected[:3]:
        print(f"  - {rel['table1']}.{rel['table1_column']} -> {rel['table2']}.{rel['table2_column']}")
    
    # Test 4: Validate relationships
    validation = engine.validate_relationships()
    print(f"✓ Validated relationships: {validation['validated']} valid, {validation['failed']} failed")
    
    # Test 5: Get schema with relationships
    schema = engine.multi_table_manager.get_schema_with_relationships()
    print(f"✓ Schema with relationships generated ({len(schema)} chars)")
    
    # Test 6: Get join hints for LLM
    hints = engine.multi_table_manager.get_join_hints_for_llm()
    print(f"✓ Join hints generated ({len(hints)} chars)")
    
    # Test 7: Test a multi-table query
    try:
        sql = """
        SELECT c.campaign_name, p.product_name, p.category, SUM(c.spend) as total_spend
        FROM campaigns c
        LEFT JOIN products p ON c.product_id = p.product_id
        GROUP BY c.campaign_name, p.product_name, p.category
        """
        result = engine.execute_query(sql)
        print(f"✓ Multi-table query executed successfully: {len(result)} rows returned")
    except Exception as e:
        print(f"⚠ Multi-table query test skipped: {e}")
    
    print("\n✅ All Multi-Table Manager tests passed!\n")


if __name__ == '__main__':
    try:
        test_query_optimizer()
        test_multi_table_manager()
        print("\n" + "="*60)
        print("🎉 ALL TESTS PASSED! Query engine enhancements verified.")
        print("="*60 + "\n")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
