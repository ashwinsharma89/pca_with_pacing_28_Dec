"""
Generate Sample Historical Campaign Data
For testing predictive analytics models
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set random seed
np.random.seed(42)

# Generate 100 historical campaigns
n_campaigns = 100

# Campaign parameters
campaigns = []

for i in range(n_campaigns):
    # Basic parameters
    budget = np.random.uniform(50000, 500000)
    duration = np.random.randint(14, 60)
    audience_size = np.random.randint(50000, 1000000)
    
    # Channels
    channel_options = ['Meta', 'Google', 'LinkedIn', 'Display', 'Snapchat']
    n_channels = np.random.randint(1, 4)
    channels = ','.join(np.random.choice(channel_options, n_channels, replace=False))
    
    # Creative and objective
    creative_type = np.random.choice(['video', 'image', 'carousel', 'collection'])
    objective = np.random.choice(['awareness', 'conversion', 'engagement', 'lead_generation'])
    
    # Start date (last 12 months)
    start_date = datetime.now() - timedelta(days=np.random.randint(0, 365))
    
    # Performance metrics (with some correlation to budget and channels)
    base_roas = np.random.uniform(1.5, 6.0)
    
    # Better performance for:
    # - Video creative (+0.5 ROAS)
    # - Conversion objective (+0.3 ROAS)
    # - Multiple channels (+0.2 ROAS per channel)
    # - Larger budgets (+0.1 ROAS per 100k)
    
    roas_boost = 0
    if creative_type == 'video':
        roas_boost += 0.5
    if objective == 'conversion':
        roas_boost += 0.3
    roas_boost += n_channels * 0.2
    roas_boost += (budget / 100000) * 0.1
    
    final_roas = base_roas + roas_boost + np.random.normal(0, 0.3)
    final_roas = max(1.0, min(8.0, final_roas))  # Clamp between 1-8
    
    # Calculate other metrics
    spend = budget * np.random.uniform(0.85, 1.0)  # 85-100% of budget spent
    revenue = spend * final_roas
    
    impressions = int(spend / np.random.uniform(5, 15) * 1000)  # CPM between $5-15
    clicks = int(impressions * np.random.uniform(0.01, 0.04))  # CTR 1-4%
    conversions = int(clicks * np.random.uniform(0.01, 0.08))  # Conv rate 1-8%
    
    cpa = spend / conversions if conversions > 0 else 0
    ctr = (clicks / impressions * 100) if impressions > 0 else 0
    conversion_rate = (conversions / clicks * 100) if clicks > 0 else 0
    
    campaigns.append({
        'campaign_id': f'CAMP_{i+1:03d}',
        'campaign_name': f'Campaign_{i+1}',
        'advertiser_id': f'ADV_{np.random.randint(1, 6):03d}',
        'budget': round(budget, 2),
        'duration': duration,
        'audience_size': audience_size,
        'channels': channels,
        'creative_type': creative_type,
        'objective': objective,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': (start_date + timedelta(days=duration)).strftime('%Y-%m-%d'),
        'spend': round(spend, 2),
        'impressions': impressions,
        'clicks': clicks,
        'conversions': conversions,
        'revenue': round(revenue, 2),
        'roas': round(final_roas, 2),
        'cpa': round(cpa, 2),
        'ctr': round(ctr, 2),
        'conversion_rate': round(conversion_rate, 2)
    })

# Create DataFrame
df = pd.DataFrame(campaigns)

# Save to CSV
output_file = 'data/historical_campaigns_sample.csv'
df.to_csv(output_file, index=False)

print(f"✅ Generated {len(df)} historical campaigns")
print(f"💾 Saved to: {output_file}")
print(f"\n📊 Summary Statistics:")
print(f"   Budget Range: ${df['budget'].min():,.0f} - ${df['budget'].max():,.0f}")
print(f"   ROAS Range: {df['roas'].min():.2f} - {df['roas'].max():.2f}")
print(f"   Avg ROAS: {df['roas'].mean():.2f}")
print(f"   Success Rate (ROAS >= 3.0): {(df['roas'] >= 3.0).mean():.1%}")
print(f"\n📁 Upload this file to the Predictive Analytics dashboard to train your model!")
