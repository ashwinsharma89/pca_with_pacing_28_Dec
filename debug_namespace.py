
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

# Set env vars to avoid startup errors
os.environ["DATABASE_URL"] = "postgresql://ashwin@localhost:5433/test_pca"
os.environ["SKIP_DOCKER"] = "1"
os.environ["OPENAI_API_KEY"] = "dummy"
os.environ["JWT_SECRET_KEY"] = "dummy_secret_for_introspection_only"

try:
    from src.api.v1 import campaigns
    print(f"Has query_engine: {hasattr(campaigns, 'query_engine')}")
    if hasattr(campaigns, 'query_engine'):
        print(f"Type: {type(campaigns.query_engine)}")
except Exception as e:
    print(f"Import failed: {e}")
