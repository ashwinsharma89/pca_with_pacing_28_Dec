import sys
import traceback
import os

print("Starting debug_import.py")
try:
    print("Importing dotenv...")
    from dotenv import load_dotenv
    load_dotenv()
    print("Importing sqlalchemy...")
    from sqlalchemy import create_engine
    
    print("Adding src to path...")
    sys.path.insert(0, os.getcwd())
    
    print("Importing User model...")
    from src.database.user_models import User
    print("Importing UserService...")
    from src.services.user_service import UserService
    
    print("✅ All imports successful")
    
    db_url = os.getenv('DATABASE_URL')
    print(f"URL: {db_url}")
    engine = create_engine(db_url)
    with engine.connect() as conn:
        print("✅ Connected to DB")
except Exception:
    print("❌ Error occurred")
    traceback.print_exc()
