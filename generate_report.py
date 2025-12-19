#!/usr/bin/env python
"""
Quick CLI tool for generating automated reports.

Usage:
    python generate_report.py daily
    python generate_report.py weekly
    python generate_report.py --date 2024-12-01
"""

import sys
import argparse
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.reporting.automated_reporter import AutomatedReporter


def main():
    parser = argparse.ArgumentParser(description='Generate automated campaign reports')
    parser.add_argument(
        'report_type',
        choices=['daily', 'weekly', 'both'],
        help='Type of report to generate'
    )
    parser.add_argument(
        '--date',
        type=str,
        help='Report date (YYYY-MM-DD), default: today'
    )
    parser.add_argument(
        '--budgets',
        type=str,
        default='config/campaign_budgets.csv',
        help='Path to campaign budgets file'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='reports/automated',
        help='Output directory for reports'
    )
    parser.add_argument(
        '--format',
        choices=['json', 'csv', 'excel', 'all'],
        default='all',
        help='Output format'
    )
    
    args = parser.parse_args()
    
    # Parse date
    if args.date:
        report_date = datetime.strptime(args.date, '%Y-%m-%d')
    else:
        report_date = datetime.now()
    
    print("=" * 60)
    print("PCA Agent - Automated Reporting")
    print("=" * 60)
    print()
    
    # Initialize reporter
    print("Initializing reporter...")
    reporter = AutomatedReporter()
    
    # Load budgets
    if Path(args.budgets).exists():
        print(f"Loading budgets from {args.budgets}...")
        reporter.load_budgets(args.budgets)
        print(f"✓ Loaded {len(reporter.budgets)} campaign budgets")
    else:
        print(f"⚠ Budget file not found: {args.budgets}")
        print("  Continuing without budget tracking...")
    
    print()
    
    # Generate reports
    reports_generated = []
    
    if args.report_type in ['daily', 'both']:
        print(f"Generating daily report for {report_date.strftime('%Y-%m-%d')}...")
        daily_report = reporter.generate_daily_report(report_date)
        
        if daily_report.get('status') != 'no_data':
            campaigns_count = len(daily_report.get('campaigns', []))
            alerts_count = len(daily_report.get('alerts', []))
            
            print(f"✓ Daily report generated")
            print(f"  - Campaigns: {campaigns_count}")
            print(f"  - Alerts: {alerts_count}")
            
            # Export formats
            if args.format in ['excel', 'all']:
                excel_path = Path(args.output) / f"daily_report_{report_date.strftime('%Y%m%d')}.xlsx"
                reporter.export_to_excel(daily_report, str(excel_path))
                print(f"  - Excel: {excel_path}")
                reports_generated.append(str(excel_path))
            
            if args.format in ['json', 'all']:
                json_path = Path(args.output) / f"daily_report_{report_date.strftime('%Y%m%d')}.json"
                print(f"  - JSON: {json_path}")
                reports_generated.append(str(json_path))
            
            if args.format in ['csv', 'all']:
                csv_path = Path(args.output) / f"daily_report_{report_date.strftime('%Y%m%d')}.csv"
                print(f"  - CSV: {csv_path}")
                reports_generated.append(str(csv_path))
            
            # Show summary
            if daily_report.get('summary'):
                summary = daily_report['summary']
                print()
                print("  Summary:")
                print(f"    Total Spend: ${summary.get('total_spend', 0):,.2f}")
                print(f"    Total Revenue: ${summary.get('total_revenue', 0):,.2f}")
                print(f"    Overall ROAS: {summary.get('overall_roas', 0):.2f}x")
                print(f"    Avg CPC: ${summary.get('avg_cpc', 0):.2f}")
                print(f"    Avg CTR: {summary.get('avg_ctr', 0):.2f}%")
            
            # Show alerts
            if alerts_count > 0:
                print()
                print("  ⚠ Alerts:")
                for alert in daily_report['alerts'][:3]:  # Show first 3
                    print(f"    - [{alert['severity'].upper()}] {alert['message']}")
                if alerts_count > 3:
                    print(f"    ... and {alerts_count - 3} more")
        else:
            print("⚠ No data available for daily report")
        
        print()
    
    if args.report_type in ['weekly', 'both']:
        print(f"Generating weekly report ending {report_date.strftime('%Y-%m-%d')}...")
        weekly_report = reporter.generate_weekly_report(report_date)
        
        if weekly_report.get('status') != 'no_data':
            campaigns_count = len(weekly_report.get('campaigns', []))
            alerts_count = len(weekly_report.get('alerts', []))
            
            print(f"✓ Weekly report generated")
            print(f"  - Period: {weekly_report['start_date']} to {weekly_report['end_date']}")
            print(f"  - Campaigns: {campaigns_count}")
            print(f"  - Alerts: {alerts_count}")
            
            # Export formats
            if args.format in ['excel', 'all']:
                excel_path = Path(args.output) / f"weekly_report_{report_date.strftime('%Y%m%d')}.xlsx"
                reporter.export_to_excel(weekly_report, str(excel_path))
                print(f"  - Excel: {excel_path}")
                reports_generated.append(str(excel_path))
            
            if args.format in ['json', 'all']:
                json_path = Path(args.output) / f"weekly_report_{report_date.strftime('%Y%m%d')}.json"
                print(f"  - JSON: {json_path}")
                reports_generated.append(str(json_path))
            
            if args.format in ['csv', 'all']:
                csv_path = Path(args.output) / f"weekly_report_{report_date.strftime('%Y%m%d')}.csv"
                print(f"  - CSV: {csv_path}")
                reports_generated.append(str(csv_path))
            
            # Show summary
            if weekly_report.get('summary'):
                summary = weekly_report['summary']
                print()
                print("  Summary:")
                print(f"    Total Spend: ${summary.get('total_spend', 0):,.2f}")
                print(f"    Total Revenue: ${summary.get('total_revenue', 0):,.2f}")
                print(f"    Overall ROAS: {summary.get('overall_roas', 0):.2f}x")
            
            # Show trends
            if weekly_report.get('trends'):
                trends = weekly_report['trends']
                print()
                print("  Trends:")
                print(f"    Spend: {trends.get('spend_change_pct', 0):+.1f}%")
                print(f"    Conversions: {trends.get('conversions_change_pct', 0):+.1f}%")
                print(f"    ROAS: {trends.get('roas_change_pct', 0):+.1f}%")
        else:
            print("⚠ No data available for weekly report")
        
        print()
    
    # Summary
    print("=" * 60)
    print(f"✓ Report generation complete!")
    print(f"  Generated {len(reports_generated)} report file(s)")
    print("=" * 60)


if __name__ == "__main__":
    main()
