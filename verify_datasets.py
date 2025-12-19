import pandas as pd

files = [
    'meta_ads_dataset.csv',
    'snapchat_ads_dataset.csv', 
    'google_ads_dataset.csv',
    'cm360_dataset.csv',
    'dv360_dataset.csv',
    'linkedin_ads_dataset.csv',
    'tradedesk_dataset.csv'
]

print('📊 FINAL DATASET COUNTS:')
print('='*60)

total = 0
for f in files:
    df = pd.read_csv(f'data/{f}')
    rows = len(df)
    total += rows
    platform = f.replace('_dataset_large.csv', '').replace('_', ' ').title()
    print(f'✅ {platform:20s}: {rows:,} rows')

print('='*60)
print(f'\n🎉 TOTAL: {total:,} rows across 7 platforms!')
print(f'📅 Date Range: 2024-06-01 to 2024-11-30 (183 days)')
print(f'📈 Average: {total//7:,} rows per platform')
