"""
Quick test to see what error we get from registration endpoint.
"""

import sys
sys.path.insert(0, '/Users/ashwin/Desktop/pca_agent copy')

from fastapi.testclient import TestClient
import os

# Set test environment
os.environ['TESTING'] = 'true'
os.environ['JWT_SECRET_KEY'] = 'test-secret-key'
os.environ['RATE_LIMIT_ENABLED'] = 'false'
os.environ['DUCKDB_AUTH_PATH'] = './data/test_auth_debug.duckdb'

from src.api.main import app

client = TestClient(app)

# Try to register a user
response = client.post(
    "/api/v1/auth/register",
    json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123!"
    }
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")
