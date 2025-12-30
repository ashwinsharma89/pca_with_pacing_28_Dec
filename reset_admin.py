import os
import bcrypt
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
db_url = os.getenv('DATABASE_URL')
engine = create_engine(db_url)

username = "admin"
password = "AdminPassword123!"
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()

print(f"Resetting admin user '{username}'...")
try:
    with engine.connect() as conn:
        # Update everything in one go
        sql = """
        UPDATE users 
        SET hashed_password = :hashed,
            failed_login_attempts = 0,
            locked_until = NULL,
            is_active = true
        WHERE username = :username
        """
        result = conn.execute(text(sql), {"hashed": hashed, "username": username})
        if result.rowcount == 0:
            print("Admin user not found, inserting...")
            insert_sql = """
            INSERT INTO users (username, email, hashed_password, role, tier, is_active, is_verified, must_change_password)
            VALUES (:username, 'admin@example.com', :hashed, 'admin', 'enterprise', true, true, false)
            """
            conn.execute(text(insert_sql), {"username": username, "hashed": hashed})
        conn.commit()
        print("✅ Admin user reset successfully")
except Exception as e:
    print(f"❌ Error: {e}")
