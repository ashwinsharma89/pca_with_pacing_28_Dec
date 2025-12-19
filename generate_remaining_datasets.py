"""
Generate Remaining Large Platform-Specific Datasets
Creates Snapchat, CM360, DV360, and Trade Desk datasets with 500-1000 rows each
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_dates(start_date, end_date):
    """Generate daily dates between start and end"""
    dates = []
    current = start_date
    while current <= end_date:
        dates.append(current)
        current += timedelta(days=1)
    return dates

def add_variance(base_value, variance=0.15):
    """Add random variance to a base value"""
    return base_value * (1 + np.random.uniform(-variance, variance))

# Date range: 6 months of daily data
start_date = datetime(2024, 6, 1)
end_date = datetime(2024, 11, 30)
dates = generate_dates(start_date, end_date)

print(f"Generating datasets with {len(dates)} days of data...")

campaigns = ['Holiday_Campaign_2024', 'Black_Friday_2024', 'Cyber_Monday_2024', 
             'Summer_Sale_2024', 'Back_To_School_2024', 'Spring_Launch_2024',
             'Valentine_Day_2024', 'New_Year_2024']

# ============================================================================
# 1. SNAPCHAT ADS DATASET
# ============================================================================
print("\n1. Generating Snapchat Ads dataset...")

placements = ['Discover', 'Stories', 'Camera', 'Spotlight']
ages = ['18-24', '25-34', '35-44']
genders = ['Male', 'Female']

snapchat_data = []
for date in dates:
    for campaign in campaigns:
        for placement in random.sample(placements, 3):  # 3 placements per campaign per day
            age = random.choice(ages)
            gender = random.choice(genders)
            
            impressions = int(add_variance(random.randint(800000, 2500000), 0.3))
            swipes = int(impressions * add_variance(0.018, 0.3))
            swipe_rate = (swipes / impressions) * 100
            video_views = int(impressions * add_variance(0.83, 0.1))
            video_view_rate = (video_views / impressions) * 100
            
            spend = swipes * add_variance(1.85, 0.2)
            ecpm = (spend / impressions) * 1000
            ecpswipe = spend / swipes if swipes > 0 else 0
            
            conversions = int(swipes * add_variance(0.092, 0.3))
            conv_rate = (conversions / swipes * 100) if swipes > 0 else 0
            revenue = conversions * add_variance(160, 0.15)
            roas = revenue / spend if spend > 0 else 0
            
            reach = int(impressions * add_variance(0.65, 0.1))
            frequency = impressions / reach
            
            snapchat_data.append({
                'Campaign_Name': campaign,
                'Ad_Squad_Name': f"{placement}_Squad",
                'Ad_Name': f"{placement}_Ad",
                'Date': date.strftime('%Y-%m-%d'),
                'Objective': random.choice(['App_Installs', 'Conversions', 'Engagement', 'Video_Views']),
                'Placement': placement,
                'Device': 'Mobile',
                'Age': age,
                'Gender': gender,
                'Impressions': impressions,
                'Swipes': swipes,
                'Swipe_Up_Rate': round(swipe_rate, 2),
                'Video_Views': video_views,
                'Video_View_Rate': round(video_view_rate, 2),
                'Quartile_1': int(video_views * 0.9),
                'Quartile_2': int(video_views * 0.8),
                'Quartile_3': int(video_views * 0.6),
                'Completion_Rate': 60.0,
                'Spend': round(spend, 2),
                'eCPM': round(ecpm, 2),
                'eCPSwipe': round(ecpswipe, 2),
                'Screen_Time_Millis': int(add_variance(8700, 0.2)),
                'Conversions': conversions,
                'Conversion_Rate': round(conv_rate, 2),
                'Revenue': round(revenue, 2),
                'ROAS': round(roas, 2),
                'Frequency': round(frequency, 2),
                'Reach': reach
            })

snapchat_df = pd.DataFrame(snapchat_data)
snapchat_df.to_csv('data/snapchat_ads_dataset_large.csv', index=False)
print(f"✅ Snapchat Ads: {len(snapchat_df)} rows")

# ============================================================================
# 2. CAMPAIGN MANAGER 360 DATASET
# ============================================================================
print("\n2. Generating CM360 dataset...")

ad_types = ['Display', 'Video', 'Native']
environments = ['Desktop', 'Mobile']
sites = ['PremiumNews.com', 'TechReview.com', 'Shopping.com', 'Lifestyle.com', 'Deals.com']

cm360_data = []
for date in dates:
    for campaign in campaigns:
        for _ in range(3):  # 3 placements per campaign per day
            ad_type = random.choice(ad_types)
            environment = random.choice(environments)
            
            impressions = int(add_variance(random.randint(1000000, 3000000), 0.3))
            clicks = int(impressions * add_variance(0.022, 0.3))
            ctr = (clicks / impressions) * 100
            
            total_conv = int(clicks * add_variance(0.075, 0.3))
            post_click = int(total_conv * 0.85)
            post_view = total_conv - post_click
            
            media_cost = clicks * add_variance(2.1, 0.2)
            revenue = total_conv * add_variance(170, 0.15)
            roas = revenue / media_cost if media_cost > 0 else 0
            
            viewable_impr = int(impressions * 0.9)
            
            cm360_data.append({
                'Campaign_Name': campaign,
                'Placement_Name': f"{ad_type}_Placement",
                'Creative_Name': f"{ad_type}_Creative",
                'Site_Name': random.choice(sites),
                'Date': date.strftime('%Y-%m-%d'),
                'Ad_Type': ad_type,
                'Environment': environment,
                'Device': environment,
                'Impressions': impressions,
                'Clicks': clicks,
                'CTR': round(ctr, 2),
                'Total_Conversions': total_conv,
                'Post_Click_Conversions': post_click,
                'Post_View_Conversions': post_view,
                'Click_Through_Conversions': post_click,
                'View_Through_Conversions': post_view,
                'Media_Cost': round(media_cost, 2),
                'Revenue': round(revenue, 2),
                'ROAS': round(roas, 2),
                'CPM': round((media_cost / impressions) * 1000, 2),
                'CPC': round(media_cost / clicks, 2) if clicks > 0 else 0,
                'CPA': round(media_cost / total_conv, 2) if total_conv > 0 else 0,
                'Viewable_Impressions': viewable_impr,
                'Measurable_Impressions': impressions,
                'Viewability_Rate': 90.0,
                'Active_View_Viewable_Impressions': viewable_impr,
                'Active_View_Measurable_Impressions': impressions,
                'Active_View_Eligible_Impressions': impressions,
                'Active_View_Avg_Time_Seconds': round(add_variance(12.5, 0.3), 1)
            })

cm360_df = pd.DataFrame(cm360_data)
cm360_df.to_csv('data/cm360_dataset_large.csv', index=False)
print(f"✅ CM360: {len(cm360_df)} rows")

# ============================================================================
# 3. DV360 DATASET
# ============================================================================
print("\n3. Generating DV360 dataset...")

exchanges = ['Google_Ad_Manager', 'YouTube', 'Hulu', 'AppNexus', 'The_Trade_Desk']
inventory_types = ['Open_Auction', 'Programmatic_Guaranteed', 'Private_Marketplace']
environments_dv = ['Display', 'Video']
devices = ['Desktop', 'Mobile', 'Connected_TV']

dv360_data = []
for date in dates:
    for campaign in campaigns:
        for _ in range(3):  # 3 line items per campaign per day
            environment = random.choice(environments_dv)
            device = random.choice(devices)
            
            impressions = int(add_variance(random.randint(1500000, 3500000), 0.3))
            clicks = int(impressions * add_variance(0.015, 0.3))
            ctr = (clicks / impressions) * 100
            
            conversions = int(clicks * add_variance(0.07, 0.3))
            post_click = int(conversions * 0.86)
            post_view = conversions - post_click
            
            media_cost = clicks * add_variance(1.95, 0.2)
            revenue = conversions * add_variance(175, 0.15)
            roas = revenue / media_cost if media_cost > 0 else 0
            
            viewable_impr = int(impressions * 0.9)
            video_completions = int(impressions * 0.6) if environment == 'Video' else 0
            
            dv360_data.append({
                'Advertiser': 'Premium_Brand_2024',
                'Insertion_Order': f"{campaign}_IO",
                'Line_Item': f"{environment}_LI",
                'Creative': f"{environment}_Creative",
                'Date': date.strftime('%Y-%m-%d'),
                'Environment': environment,
                'Exchange': random.choice(exchanges),
                'Device': device,
                'Inventory_Type': random.choice(inventory_types),
                'Impressions': impressions,
                'Clicks': clicks,
                'CTR': round(ctr, 2),
                'Conversions': conversions,
                'Post_Click_Conv': post_click,
                'Post_View_Conv': post_view,
                'Revenue_Adv_Currency': round(revenue, 2),
                'Media_Cost_Adv_Currency': round(media_cost, 2),
                'ROAS': round(roas, 2),
                'CPM': round((media_cost / impressions) * 1000, 2),
                'CPC': round(media_cost / clicks, 2) if clicks > 0 else 0,
                'CPA': round(media_cost / conversions, 2) if conversions > 0 else 0,
                'Viewable_Impressions': viewable_impr,
                'Measurable_Impressions': impressions,
                'Viewability_Percent': 90.0,
                'Active_View_Viewable_Impressions': viewable_impr,
                'Active_View_Measurable_Impressions': impressions,
                'Video_Completions': video_completions,
                'Video_Completion_Rate': 60.0 if video_completions > 0 else 0,
                'Video_Quartile_1': int(impressions * 0.9) if environment == 'Video' else 0,
                'Video_Quartile_2': int(impressions * 0.8) if environment == 'Video' else 0,
                'Video_Quartile_3': int(impressions * 0.6) if environment == 'Video' else 0
            })

dv360_df = pd.DataFrame(dv360_data)
dv360_df.to_csv('data/dv360_dataset_large.csv', index=False)
print(f"✅ DV360: {len(dv360_df)} rows")

# ============================================================================
# 4. THE TRADE DESK DATASET
# ============================================================================
print("\n4. Generating The Trade Desk dataset...")

channels = ['Display', 'Video', 'Native']
environments_ttd = ['Web', 'App', 'CTV']
data_providers = ['LiveRamp', 'Neustar', 'Experian', 'Oracle']
audience_segments = ['In_Market_Shoppers', 'Lookalike_Purchasers', 'Contextual_Shopping', 
                     'High_Intent_Buyers', 'Behavioral_Shoppers', 'Geo_Proximity']

tradedesk_data = []
for date in dates:
    for campaign in campaigns:
        for _ in range(3):  # 3 ad groups per campaign per day
            channel = random.choice(channels)
            environment = random.choice(environments_ttd)
            
            impressions = int(add_variance(random.randint(1200000, 3000000), 0.3))
            clicks = int(impressions * add_variance(0.016, 0.3))
            ctr = (clicks / impressions) * 100
            
            conversions = int(clicks * add_variance(0.073, 0.3))
            post_click = int(conversions * 0.84)
            post_view = conversions - post_click
            conv_rate = (conversions / clicks * 100) if clicks > 0 else 0
            
            media_cost = clicks * add_variance(2.0, 0.2)
            revenue = conversions * add_variance(168, 0.15)
            roas = revenue / media_cost if media_cost > 0 else 0
            
            reach = int(impressions * add_variance(0.62, 0.1))
            unique_reach = int(reach * 0.9)
            frequency = impressions / reach
            
            viewable_impr = int(impressions * 0.9)
            video_completions = int(impressions * 0.6) if channel == 'Video' else 0
            
            tradedesk_data.append({
                'Advertiser': 'Premium_Retail_2024',
                'Campaign': campaign,
                'Ad_Group': f"{channel}_AG",
                'Creative': f"{channel}_Creative",
                'Date': date.strftime('%Y-%m-%d'),
                'Channel': channel,
                'Device': random.choice(['Desktop', 'Mobile', 'Connected_TV']),
                'Environment': environment,
                'Data_Provider': random.choice(data_providers),
                'Audience_Segment': random.choice(audience_segments),
                'Impressions': impressions,
                'Clicks': clicks,
                'CTR': round(ctr, 2),
                'Conversions': conversions,
                'Post_Click_Conv': post_click,
                'Post_View_Conv': post_view,
                'Conversion_Rate': round(conv_rate, 2),
                'Media_Cost': round(media_cost, 2),
                'Revenue': round(revenue, 2),
                'ROAS': round(roas, 2),
                'eCPM': round((media_cost / impressions) * 1000, 2),
                'eCPC': round(media_cost / clicks, 2) if clicks > 0 else 0,
                'eCPA': round(media_cost / conversions, 2) if conversions > 0 else 0,
                'Viewable_Impressions': viewable_impr,
                'Measurable_Impressions': impressions,
                'Viewability_Rate': 90.0,
                'Video_Completions': video_completions,
                'Video_Completion_Rate': 60.0 if video_completions > 0 else 0,
                'Frequency': round(frequency, 2),
                'Reach': reach,
                'Unique_Reach': unique_reach
            })

tradedesk_df = pd.DataFrame(tradedesk_data)
tradedesk_df.to_csv('data/tradedesk_dataset_large.csv', index=False)
print(f"✅ The Trade Desk: {len(tradedesk_df)} rows")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*60)
print("📊 REMAINING DATASETS GENERATION COMPLETE")
print("="*60)
print(f"\n✅ Snapchat Ads: {len(snapchat_df):,} rows")
print(f"✅ CM360: {len(cm360_df):,} rows")
print(f"✅ DV360: {len(dv360_df):,} rows")
print(f"✅ The Trade Desk: {len(tradedesk_df):,} rows")
print(f"\n📅 Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
print(f"📆 Total Days: {len(dates)}")
print(f"\n💾 All files saved to data/ directory with '_large' suffix")

# Calculate total
print("\n" + "="*60)
print("📊 COMPLETE DATASET SUMMARY")
print("="*60)
total_rows = len(snapchat_df) + len(cm360_df) + len(dv360_df) + len(tradedesk_df)
print(f"\n✅ Total Rows (4 platforms): {total_rows:,}")
print(f"✅ Combined with previous 3 platforms: ~{total_rows + 11712:,} rows")
print("\n🎉 All 7 platform datasets are ready for training!")
