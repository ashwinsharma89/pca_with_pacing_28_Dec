import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = "http://localhost:8000/api/v1"

def test_global_analysis():
    print("🚀 Starting Global Analysis Test...")
    
    # Check if server is running
    try:
        requests.get("http://localhost:8000/health", timeout=5)
    except Exception as e:
        print(f"❌ Server is not running at http://localhost:8000: {e}")
        return

    payload = {
        "use_rag_summary": True,
        "include_benchmarks": True,
        "analysis_depth": "standard",
        "include_recommendations": True
    }
    
    # We might need an auth token if protected
    headers = {
        "Content-Type": "application/json"
    }
    
    # Using retrieved token
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsInRpZXIiOiJlbnRlcnByaXNlIiwiZXhwIjoxNzY3MDIxODgyfQ.s7m60B0OfZMYlTa2OBjuMgZ1QLf6kifkvGcydVbw3bY"
    if token:
        headers["Authorization"] = f"Bearer {token}"

    print(f"📡 Calling {API_URL}/campaigns/analyze/global...")
    try:
        response = requests.post(f"{API_URL}/campaigns/analyze/global", json=payload, headers=headers, timeout=120)
        response.raise_for_status()
        result = response.json()
        
        print("\n✅ Analysis Request Successful!")
        
        exec_summary = result.get("executive_summary", {})
        print(f"\n📝 BRIEF SUMMARY ({len(exec_summary.get('brief', ''))} chars):")
        print("-" * 40)
        print(exec_summary.get("brief", "MISSING"))
        print("-" * 40)
        
        print(f"\n📝 DETAILED SUMMARY ({len(exec_summary.get('detailed', ''))} chars):")
        print("-" * 40)
        print(exec_summary.get("detailed", "MISSING")[:500] + "...")
        print("-" * 40)
        
        if exec_summary.get("rag_metadata"):
            print("\n🤖 RAG Metadata:")
            print(json.dumps(exec_summary["rag_metadata"], indent=2))
            
    except Exception as e:
        print(f"❌ Error during analysis call: {e}")
        if 'response' in locals():
            print(f"Response body: {response.text}")

if __name__ == "__main__":
    test_global_analysis()
