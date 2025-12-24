import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")
engine = create_engine(db_url)

with engine.connect() as conn:
    result = conn.execute(text("SELECT username, email, failed_login_attempts, locked_until, is_active FROM users WHERE username='ashwin' OR email='ashwin'")).fetchone()
    if result:
        print(f"User found: {result}")
    else:
        print("User NOT found")
