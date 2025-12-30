import os, sys, bcrypt
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
sys.path.insert(0, os.getcwd())
engine = create_engine(os.getenv('DATABASE_URL'))

print("Verifying admin account status...", flush=True)
with engine.connect() as conn:
    sql = "SELECT hashed_password, failed_login_attempts, locked_until, is_active FROM users WHERE username = 'admin'"
    res = conn.execute(text(sql)).first()
    if res:
        hp, fla, lu, ia = res
        print(f"Hash: {hp[:15]}...")
        print(f"Failures: {fla}")
        print(f"Locked until: {lu}")
        print(f"Is Active: {ia}")
        is_valid = bcrypt.checkpw('AdminPassword123!'.encode(), hp.encode())
        print(f"✅ Password Valid: {is_valid}")
    else:
        print("❌ Admin user not found!")
