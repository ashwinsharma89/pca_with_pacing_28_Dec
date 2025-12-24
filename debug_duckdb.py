"""
Debug script to check what's in the DuckDB auth database.
"""

import sys
sys.path.insert(0, '/Users/ashwin/Desktop/pca_agent copy')

import duckdb

# Connect to auth database
conn = duckdb.connect('data/auth.duckdb')

# Check what users exist
print("=" * 60)
print("Users in DuckDB Auth Database:")
print("=" * 60)

users = conn.execute("""
    SELECT id, email, username, is_active, is_superuser, created_at
    FROM users
    ORDER BY id
""").fetchall()

if not users:
    print("No users found in database")
else:
    for user in users:
        print(f"\nID: {user[0]}")
        print(f"Email: {user[1]}")
        print(f"Username: {user[2]}")
        print(f"Active: {user[3]}")
        print(f"Superuser: {user[4]}")
        print(f"Created: {user[5]}")
        print("-" * 40)

print(f"\nTotal users: {len(users)}")
print("=" * 60)

conn.close()
