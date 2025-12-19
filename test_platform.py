
import os
import sys
sys.path.append(os.getcwd())

from src.database.connection import get_db_session
from src.database.repositories import CampaignRepository

session = get_db_session()
repo = CampaignRepository(session)

# Test the platform master query
print("Testing get_grouped_metrics for platform...")
result = repo.get_grouped_metrics('platform', ['spend', 'clicks', 'impressions'])
print(f"Returned {len(result)} rows")
for r in result[:5]:
    print(f"  {r}")

session.close()
