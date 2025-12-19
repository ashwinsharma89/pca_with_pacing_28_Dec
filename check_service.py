from src.database.connection import get_db
from src.services.campaign_service import CampaignService

# Mock DB session (just a dummy object since we are testing class structure)
class MockDB: pass

def test_service():
    print("Testing CampaignService...")
    db = MockDB()
    
    # Mock repos
    class MockRepo:
        def __init__(self, *args, **kwargs): pass
        
    service = CampaignService(db, analysis_repo=MockRepo(), context_repo=MockRepo())
    
    if hasattr(service, 'list_campaigns'):
        print("✅ list_campaigns method exists")
        try:
            campaigns = service.list_campaigns()
            print(f"✅ list_campaigns execution successful: {len(campaigns)} items")
        except Exception as e:
            print(f"❌ list_campaigns execution failed: {e}")
    else:
        print("❌ list_campaigns method MISSING")

if __name__ == "__main__":
    test_service()
