import requests
import json
import pandas as pd
import os

# Base URL
BASE_URL = "http://localhost:8000/api/v1/campaigns"

def get_auth_token():
    # Attempt to get token from a local file or env
    # For now, let's assume we can bypass or use a dummy if the server allows it
    # Or we can check existing login flow
    return None

def test_filters():
    print("Testing /filters endpoint...")
    response = requests.get(f"{BASE_URL}/filters", headers={"Authorization": f"Bearer dummy_token"})
    if response.status_code == 200:
        filters = response.json()
        print("Success! Available filters:", list(filters.keys()))
        for k, v in filters.items():
            print(f"  {k}: {len(v)} options")
    else:
        print(f"Failed to get filters: {response.status_code} - {response.text}")

def test_visualizations_with_filter():
    print("\nTesting /visualizations with filter...")
    # Try a common filter if available
    params = {"platforms": "Google"} 
    response = requests.get(f"{BASE_URL}/visualizations", params=params, headers={"Authorization": f"Bearer dummy_token"})
    if response.status_code == 200:
        data = response.json()
        print("Success! Data received.")
        if data.get('platform'):
            print(f"  Platform data rows: {len(data['platform'])}")
    else:
        print(f"Failed to get visualizations: {response.status_code} - {response.text}")

if __name__ == "__main__":
    # Note: This requires the backend to be running and bypassing auth for dummy_token or having a real one.
    # Since I cannot easily get a real token without browser interaction, I'll rely on browser verification.
    pass
