"""
Generate comprehensive analysis report from RAG comparison logs.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.comparison_logger import ComparisonLogger
from loguru import logger


def main():
    """Generate and display analysis report."""
    
    logger.info("=" * 80)
    logger.info("GENERATING RAG COMPARISON ANALYSIS REPORT")
    logger.info("=" * 80)
    
    # Initialize logger
    comparison_logger = ComparisonLogger()
    
    # Get summary statistics
    logger.info("\n📊 Fetching summary statistics...")
    stats = comparison_logger.get_summary_stats()
    
    print("\n" + "=" * 80)
    print("RAG VS STANDARD EXECUTIVE SUMMARY - ANALYSIS REPORT")
    print("=" * 80)
    
    if 'error' in stats:
        print(f"\nError: {stats['error']}")
        return
    
    if stats.get('total_comparisons', 0) == 0:
        print("\nNo comparison data available yet.")
        print("Run test_rag_integration.py or use the Streamlit UI toggle to generate comparisons.")
        return
    
    # Display statistics
    print(f"\nPERFORMANCE METRICS")
    print("-" * 80)
    print(f"Total Comparisons: {stats.get('total_comparisons', 0)}")
    print(f"\nToken Usage:")
    print(f"  Average Token Increase: {stats.get('avg_token_increase_pct', 0):.1f}%")
    print(f"\nCost Analysis:")
    print(f"  Standard Avg Cost: ${stats.get('avg_standard_cost', 0):.4f}")
    print(f"  RAG Avg Cost: ${stats.get('avg_rag_cost', 0):.4f}")
    print(f"  Average Cost Increase: {stats.get('avg_cost_increase_pct', 0):.1f}%")
    print(f"\nLatency Analysis:")
    print(f"  Standard Avg Latency: {stats.get('avg_standard_latency', 0):.2f}s")
    print(f"  RAG Avg Latency: {stats.get('avg_rag_latency', 0):.2f}s")
    print(f"  Average Latency Increase: {stats.get('avg_latency_increase_pct', 0):.1f}%")
    print(f"\nKnowledge Retrieval:")
    print(f"  Average Knowledge Sources: {stats.get('avg_rag_sources', 0):.1f}")
    
    # User feedback
    if stats.get('total_feedback', 0) > 0:
        print(f"\nUSER FEEDBACK")
        print("-" * 80)
        print(f"Total Feedback Responses: {stats.get('total_feedback', 0)}")
        print(f"RAG Preference: {stats.get('rag_preference_pct', 0):.1f}%")
        print(f"Standard Preference: {stats.get('standard_preference_pct', 0):.1f}%")
        
        if 'avg_quality_rating' in stats:
            print(f"Average Quality Rating: {stats.get('avg_quality_rating', 0):.2f}/5")
        if 'avg_usefulness_rating' in stats:
            print(f"Average Usefulness Rating: {stats.get('avg_usefulness_rating', 0):.2f}/5")
    else:
        print(f"\nUSER FEEDBACK")
        print("-" * 80)
        print("No user feedback collected yet.")
        print("Use the Streamlit UI feedback buttons to provide feedback.")
    
    # Generate detailed report
    print("\nGenerating detailed markdown report...")
    report_path = comparison_logger.export_analysis_report()
    
    print(f"\nDETAILED REPORT")
    print("-" * 80)
    print(f"Report saved to: {report_path}")
    print(f"\nOpen the report file to view detailed analysis with recommendations.")
    
    print("\n" + "=" * 80)
    print("Analysis report generated successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
