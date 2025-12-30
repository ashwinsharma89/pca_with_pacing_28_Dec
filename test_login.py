import os
import sys
import bcrypt

# Minimal imports
print("START", flush=True)
try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    print("IMPORTS DONE", flush=True)
    
    sys.path.insert(0, os.getcwd())
    from src.database.user_models import User
    from src.services.user_service import UserService
    from dotenv import load_dotenv
    load_dotenv()
    
    db_url = os.getenv('DATABASE_URL')
    print(f"URL: {db_url[:20]}...", flush=True)
    
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    user = db.query(User).filter(User.username == 'admin').first()
    if user:
        print(f"USER: {user.username}", flush=True)
        print(f"HASH: {user.hashed_password}", flush=True)
        is_valid = bcrypt.checkpw('AdminPassword123!'.encode(), user.hashed_password.encode())
        print(f"VALID: {is_valid}", flush=True)
    else:
        print("MISSING", flush=True)
    db.close()
except Exception as e:
    print(f"ERROR: {e}", flush=True)
print("FINISH", flush=True)
