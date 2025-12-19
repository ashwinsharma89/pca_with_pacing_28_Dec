
import time
import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

from src.database.connection import get_db_session
from src.database.repositories import CampaignRepository

def benchmark():
    session = get_db_session()
    repo = CampaignRepository(session)
    
    count = repo.count_all()
    print(f"Total Campaigns: {count}")
    
    dimensions = ['platform', 'channel', 'funnel_stage', 'objective']
    metrics = ['spend', 'conversions', 'clicks', 'impressions']
    
    for dim in dimensions:
        start = time.time()
        print(f"Querying grouped by {dim}...")
        res = repo.get_grouped_metrics(dim, metrics)
        end = time.time()
        print(f"  - {dim} took {(end - start)*1000:.2f}ms (returned {len(res)} rows)")
        
    session.close()

if __name__ == "__main__":
    benchmark()
