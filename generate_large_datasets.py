"""
Generate Large Platform-Specific Datasets
Creates 500-1000 rows per platform with daily data across multiple months
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

# ============================================================================
# 1. META ADS DATASET (Expanded)
# ============================================================================
print("\n1. Generating Meta Ads dataset...")

campaigns = ['Holiday_Campaign_2024', 'Black_Friday_2024', 'Cyber_Monday_2024', 
             'Summer_Sale_2024', 'Back_To_School_2024', 'Spring_Launch_2024',
             'Valentine_Day_2024', 'New_Year_2024', 'Q3_Promo_2024', 'Flash_Sale_2024']

ad_sets = ['Awareness_Set', 'Consideration_Set', 'Conversion_Set', 'Retargeting_Set', 
           'Lookalike_Set', 'Engagement_Set', 'Traffic_Set']

placements = ['Facebook_Feed', 'Instagram_Stories', 'Instagram_Feed', 'Instagram_Reels',
              'Facebook_Marketplace', 'Instagram_Explore', 'Audience_Network']

devices = ['Mobile', 'Desktop']
ages = ['18-24', '25-34', '35-44', '45-54']
genders = ['Male', 'Female']

meta_data = []
for date in dates:
    for campaign in campaigns[:8]:  # Use 8 campaigns
        for placement in random.sample(placements, 3):  # 3 placements per campaign per day
            ad_set = random.choice(ad_sets)
            device = random.choice(devices)
            age = random.choice(ages)
            gender = random.choice(genders)
            
            # Base metrics with daily variance
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
            
            # Video metrics (if applicable)
            video_views = int(impressions * add_variance(0.65, 0.2)) if 'Stories' in placement or 'Reels' in placement else 0
            video_watch_time = add_variance(18, 0.3) if video_views > 0 else 0
            
            # Engagement
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
meta_df.to_csv('data/meta_ads_dataset_large.csv', index=False)
print(f"✅ Meta Ads: {len(meta_df)} rows")

# ============================================================================
# 2. GOOGLE ADS DATASET (Expanded)
# ============================================================================
print("\n2. Generating Google Ads dataset...")

keywords_data = {
    'Holiday_Shopping_2024': [('holiday gifts', 'Broad'), ('christmas presents', 'Phrase'), ('best deals', 'Exact')],
    'Black_Friday_2024': [('black friday deals', 'Exact'), ('black friday sale', 'Phrase'), ('bf deals', 'Broad')],
    'Cyber_Monday_2024': [('cyber monday tech', 'Exact'), ('laptop deals', 'Phrase'), ('tech sale', 'Broad')],
    'Summer_Sale_2024': [('summer sale', 'Broad'), ('summer deals', 'Phrase'), ('summer clothing', 'Exact')],
    'Back_To_School_2024': [('school supplies', 'Exact'), ('back to school', 'Phrase'), ('student laptop', 'Broad')],
    'Spring_Sale_2024': [('spring sale', 'Broad'), ('spring deals', 'Phrase'), ('spring fashion', 'Exact')],
    'Valentine_Day_2024': [('valentine gifts', 'Exact'), ('valentine presents', 'Phrase'), ('valentine flowers', 'Broad')],
    'New_Year_2024': [('new year deals', 'Broad'), ('new year sale', 'Phrase'), ('fitness equipment', 'Exact')]
}

google_data = []
for date in dates:
    for campaign, keywords in list(keywords_data.items())[:8]:
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
google_df.to_csv('data/google_ads_dataset_large.csv', index=False)
print(f"✅ Google Ads: {len(google_df)} rows")

# ============================================================================
# 3. LINKEDIN ADS DATASET (Expanded)
# ============================================================================
print("\n3. Generating LinkedIn Ads dataset...")

job_functions = ['IT', 'Marketing', 'Sales', 'HR', 'Finance', 'Operations']
seniorities = ['Manager', 'Director', 'VP', 'C-Level']
company_sizes = ['501-1000', '1001-5000', '5001-10000', '10001+']
industries = ['Technology', 'Marketing', 'Consulting', 'Education', 'Healthcare']

linkedin_data = []
for date in dates:
    for campaign in campaigns[:8]:
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
linkedin_df.to_csv('data/linkedin_ads_dataset_large.csv', index=False)
print(f"✅ LinkedIn Ads: {len(linkedin_df)} rows")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*60)
print("📊 DATASET GENERATION COMPLETE")
print("="*60)
print(f"\n✅ Meta Ads: {len(meta_df):,} rows")
print(f"✅ Google Ads: {len(google_df):,} rows")
print(f"✅ LinkedIn Ads: {len(linkedin_df):,} rows")
print(f"\n📅 Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
print(f"📆 Total Days: {len(dates)}")
print(f"\n💾 Files saved to data/ directory with '_large' suffix")
print("\nNote: Run this script again to generate Snapchat, CM360, DV360, and Trade Desk datasets")
