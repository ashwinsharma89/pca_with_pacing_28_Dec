"""
Generate Platform-Specific Datasets with Exactly 2000 Rows Each
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

# Date range: ~100 days to get 2000 rows with 10 campaigns × 2 variations
start_date = datetime(2024, 6, 1)
end_date = datetime(2024, 9, 8)  # 100 days
dates = generate_dates(start_date, end_date)

print(f"Generating datasets with {len(dates)} days of data...")
print(f"Target: 2000 rows per platform\n")

campaigns = ['Holiday_Campaign_2024', 'Black_Friday_2024', 'Cyber_Monday_2024', 
             'Summer_Sale_2024', 'Back_To_School_2024', 'Spring_Launch_2024',
             'Valentine_Day_2024', 'New_Year_2024', 'Q3_Promo_2024', 'Flash_Sale_2024']

# ============================================================================
# 1. META ADS - 2000 rows
# ============================================================================
print("1. Generating Meta Ads dataset (2000 rows)...")

placements = ['Facebook_Feed', 'Instagram_Stories', 'Instagram_Feed', 'Instagram_Reels']
devices = ['Mobile', 'Desktop']
ages = ['18-24', '25-34', '35-44', '45-54']
genders = ['Male', 'Female']

meta_data = []
for date in dates:
    for campaign in campaigns:  # 10 campaigns
        for placement in random.sample(placements, 2):  # 2 placements per campaign per day
            ad_set = random.choice(['Awareness_Set', 'Conversion_Set', 'Retargeting_Set'])
            device = random.choice(devices)
            age = random.choice(ages)
            gender = random.choice(genders)
            
            impressions = int(add_variance(random.randint(500000, 2000000), 0.3))
            reach = int(impressions * add_variance(0.75, 0.1))
            frequency = impressions / reach
            clicks = int(impressions * add_variance(0.02, 0.3))
            ctr = (clicks / impressions) * 100
            link_clicks = int(clicks * add_variance(0.85, 0.1))
            spend = clicks * add_variance(2.2, 0.2)
            cpc = spend / clicks if clicks > 0 else 0
            
            conversions = int(clicks * add_variance(0.08, 0.3))
            revenue = conversions * add_variance(145, 0.2)
            roas = revenue / spend if spend > 0 else 0
            aov = revenue / conversions if conversions > 0 else 0
            
            video_views = int(impressions * add_variance(0.65, 0.2)) if 'Stories' in placement or 'Reels' in placement else 0
            video_watch_time = add_variance(18, 0.3) if video_views > 0 else 0
            
            engagement = int(impressions * add_variance(0.005, 0.3))
            reactions = int(engagement * add_variance(0.5, 0.2))
            comments = int(engagement * add_variance(0.1, 0.3))
            shares = int(engagement * add_variance(0.05, 0.3))
            
            meta_data.append({
                'Campaign_Name': campaign,
                'Ad_Set_Name': ad_set,
                'Ad_Name': f"{placement}_Ad",
                'Date': date.strftime('%Y-%m-%d'),
                'Objective': random.choice(['Conversions', 'Brand_Awareness', 'Traffic']),
                'Placement': placement,
                'Device': device,
                'Age': age,
                'Gender': gender,
                'Impressions': impressions,
                'Reach': reach,
                'Frequency': round(frequency, 2),
                'Clicks': clicks,
                'CTR': round(ctr, 2),
                'Link_Clicks': link_clicks,
                'CPC': round(cpc, 2),
                'Spend': round(spend, 2),
                'Conversions': conversions,
                'Revenue': round(revenue, 2),
                'ROAS': round(roas, 2),
                'AOV': round(aov, 2),
                'Video_Views': video_views,
                'Video_Avg_Watch_Time': round(video_watch_time, 1),
                'Engagement': engagement,
                'Post_Reactions': reactions,
                'Post_Comments': comments,
                'Post_Shares': shares
            })

meta_df = pd.DataFrame(meta_data)
meta_df.to_csv('data/meta_ads_dataset.csv', index=False)
print(f"✅ Meta Ads: {len(meta_df)} rows")

# ============================================================================
# 2. SNAPCHAT ADS - 2000 rows
# ============================================================================
print("2. Generating Snapchat Ads dataset (2000 rows)...")

snap_placements = ['Discover', 'Stories', 'Camera', 'Spotlight']

snapchat_data = []
for date in dates:
    for campaign in campaigns:
        for placement in random.sample(snap_placements, 2):
            age = random.choice(['18-24', '25-34', '35-44'])
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
snapchat_df.to_csv('data/snapchat_ads_dataset.csv', index=False)
print(f"✅ Snapchat Ads: {len(snapchat_df)} rows")

# ============================================================================
# 3. GOOGLE ADS - 2000 rows
# ============================================================================
print("3. Generating Google Ads dataset (2000 rows)...")

keywords_data = {
    'Holiday_Shopping_2024': [('holiday gifts', 'Broad'), ('christmas presents', 'Phrase')],
    'Black_Friday_2024': [('black friday deals', 'Exact'), ('black friday sale', 'Phrase')],
    'Cyber_Monday_2024': [('cyber monday tech', 'Exact'), ('laptop deals', 'Phrase')],
    'Summer_Sale_2024': [('summer sale', 'Broad'), ('summer deals', 'Phrase')],
    'Back_To_School_2024': [('school supplies', 'Exact'), ('back to school', 'Phrase')],
    'Spring_Launch_2024': [('spring sale', 'Broad'), ('spring deals', 'Phrase')],
    'Valentine_Day_2024': [('valentine gifts', 'Exact'), ('valentine presents', 'Phrase')],
    'New_Year_2024': [('new year deals', 'Broad'), ('new year sale', 'Phrase')],
    'Q3_Promo_2024': [('summer promo', 'Phrase'), ('q3 deals', 'Broad')],
    'Flash_Sale_2024': [('flash sale', 'Exact'), ('limited time', 'Phrase')]
}

google_data = []
for date in dates:
    for campaign, keywords in keywords_data.items():
        for keyword, match_type in keywords:
            device = random.choice(['Mobile', 'Desktop'])
            age = random.choice(ages)
            gender = random.choice(genders)
            
            impressions = int(add_variance(random.randint(300000, 1000000), 0.3))
            clicks = int(impressions * add_variance(0.025, 0.3))
            ctr = (clicks / impressions) * 100
            avg_cpc = add_variance(2.0, 0.25)
            cost = clicks * avg_cpc
            
            conversions = int(clicks * add_variance(0.085, 0.3))
            conv_rate = (conversions / clicks * 100) if clicks > 0 else 0
            conv_value = conversions * add_variance(165, 0.2)
            roas = conv_value / cost if cost > 0 else 0
            
            quality_score = random.choice([7, 8, 9, 10])
            
            google_data.append({
                'Campaign_Name': campaign,
                'Ad_Group_Name': f"{keyword.split()[0]}_AG",
                'Keyword': keyword,
                'Match_Type': match_type,
                'Date': date.strftime('%Y-%m-%d'),
                'Network': random.choice(['Search', 'Shopping']),
                'Device': device,
                'Location': 'United States',
                'Age': age,
                'Gender': gender,
                'Impressions': impressions,
                'Clicks': clicks,
                'CTR': round(ctr, 2),
                'Avg_CPC': round(avg_cpc, 2),
                'Cost': round(cost, 2),
                'Conversions': conversions,
                'Conv_Rate': round(conv_rate, 2),
                'Cost_Per_Conv': round(cost/conversions, 2) if conversions > 0 else 0,
                'Conv_Value': round(conv_value, 2),
                'ROAS': round(roas, 2),
                'Quality_Score': quality_score,
                'Impression_Share': round(add_variance(75, 0.15), 1),
                'Search_Impr_Share': round(add_variance(73, 0.15), 1),
                'Top_Impr_Rate': round(add_variance(68, 0.15), 1)
            })

google_df = pd.DataFrame(google_data)
google_df.to_csv('data/google_ads_dataset.csv', index=False)
print(f"✅ Google Ads: {len(google_df)} rows")

# ============================================================================
# 4. CM360 - 2000 rows
# ============================================================================
print("4. Generating CM360 dataset (2000 rows)...")

ad_types = ['Display', 'Video', 'Native']
environments = ['Desktop', 'Mobile']
sites = ['PremiumNews.com', 'TechReview.com', 'Shopping.com', 'Lifestyle.com']

cm360_data = []
for date in dates:
    for campaign in campaigns:
        for ad_type in random.sample(ad_types, 2):
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
cm360_df.to_csv('data/cm360_dataset.csv', index=False)
print(f"✅ CM360: {len(cm360_df)} rows")

# ============================================================================
# 5. DV360 - 2000 rows
# ============================================================================
print("5. Generating DV360 dataset (2000 rows)...")

exchanges = ['Google_Ad_Manager', 'YouTube', 'Hulu', 'AppNexus']
inventory_types = ['Open_Auction', 'Programmatic_Guaranteed', 'Private_Marketplace']
environments_dv = ['Display', 'Video']
devices_dv = ['Desktop', 'Mobile', 'Connected_TV']

dv360_data = []
for date in dates:
    for campaign in campaigns:
        for environment in random.sample(environments_dv, 2):
            device = random.choice(devices_dv)
            
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
dv360_df.to_csv('data/dv360_dataset.csv', index=False)
print(f"✅ DV360: {len(dv360_df)} rows")

# ============================================================================
# 6. LINKEDIN - 2000 rows
# ============================================================================
print("6. Generating LinkedIn Ads dataset (2000 rows)...")

job_functions = ['IT', 'Marketing', 'Sales', 'HR', 'Finance', 'Operations']
seniorities = ['Manager', 'Director', 'VP', 'C-Level']
company_sizes = ['501-1000', '1001-5000', '5001-10000', '10001+']
industries = ['Technology', 'Marketing', 'Consulting', 'Education']

linkedin_data = []
for date in dates:
    for campaign in campaigns:
        for _ in range(2):  # 2 variations per campaign per day
            job_func = random.choice(job_functions)
            seniority = random.choice(seniorities)
            
            impressions = int(add_variance(random.randint(200000, 600000), 0.3))
            clicks = int(impressions * add_variance(0.028, 0.3))
            ctr = (clicks / impressions) * 100
            spend = clicks * add_variance(2.45, 0.2)
            cpc = spend / clicks if clicks > 0 else 0
            
            conversions = int(clicks * add_variance(0.072, 0.3))
            conv_rate = (conversions / clicks * 100) if clicks > 0 else 0
            revenue = conversions * add_variance(190, 0.15)
            roas = revenue / spend if spend > 0 else 0
            
            linkedin_data.append({
                'Campaign_Group': f"{campaign.split('_')[0]}_Group",
                'Campaign_Name': campaign,
                'Ad_Name': f"{job_func}_Ad",
                'Date': date.strftime('%Y-%m-%d'),
                'Objective': random.choice(['Lead_Generation', 'Conversions', 'Brand_Awareness']),
                'Ad_Format': random.choice(['Single_Image', 'Carousel', 'Video', 'Sponsored_Content']),
                'Device': random.choice(['Desktop', 'Mobile']),
                'Job_Function': job_func,
                'Seniority': seniority,
                'Company_Size': random.choice(company_sizes),
                'Industry': random.choice(industries),
                'Impressions': impressions,
                'Clicks': clicks,
                'CTR': round(ctr, 2),
                'Conversions': conversions,
                'Conversion_Rate': round(conv_rate, 2),
                'Spend': round(spend, 2),
                'CPC': round(cpc, 2),
                'Revenue': round(revenue, 2),
                'ROAS': round(roas, 2),
                'Leads': conversions,
                'Lead_Form_Completion_Rate': round(add_variance(71, 0.1), 2),
                'Engagement_Rate': round(add_variance(3.6, 0.2), 2)
            })

linkedin_df = pd.DataFrame(linkedin_data)
linkedin_df.to_csv('data/linkedin_ads_dataset.csv', index=False)
print(f"✅ LinkedIn Ads: {len(linkedin_df)} rows")

# ============================================================================
# 7. THE TRADE DESK - 2000 rows
# ============================================================================
print("7. Generating The Trade Desk dataset (2000 rows)...")

channels = ['Display', 'Video', 'Native']
environments_ttd = ['Web', 'App', 'CTV']
data_providers = ['LiveRamp', 'Neustar', 'Experian', 'Oracle']
audience_segments = ['In_Market_Shoppers', 'Lookalike_Purchasers', 'Contextual_Shopping', 
                     'High_Intent_Buyers', 'Behavioral_Shoppers']

tradedesk_data = []
for date in dates:
    for campaign in campaigns:
        for channel in random.sample(channels, 2):
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
tradedesk_df.to_csv('data/tradedesk_dataset.csv', index=False)
print(f"✅ The Trade Desk: {len(tradedesk_df)} rows")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*60)
print("📊 DATASET GENERATION COMPLETE")
print("="*60)
print(f"\n✅ Meta Ads: {len(meta_df):,} rows")
print(f"✅ Snapchat Ads: {len(snapchat_df):,} rows")
print(f"✅ Google Ads: {len(google_df):,} rows")
print(f"✅ CM360: {len(cm360_df):,} rows")
print(f"✅ DV360: {len(dv360_df):,} rows")
print(f"✅ LinkedIn Ads: {len(linkedin_df):,} rows")
print(f"✅ The Trade Desk: {len(tradedesk_df):,} rows")

total = len(meta_df) + len(snapchat_df) + len(google_df) + len(cm360_df) + len(dv360_df) + len(linkedin_df) + len(tradedesk_df)
print(f"\n🎉 TOTAL: {total:,} rows across 7 platforms!")
print(f"📅 Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
print(f"📆 Total Days: {len(dates)}")
print(f"\n💾 Files saved to data/ directory (overwriting previous versions)")
