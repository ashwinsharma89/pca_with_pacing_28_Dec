
import requests
import json
import sys
import time

def get_token():
    try:
        resp = requests.post('http://localhost:8000/api/v1/auth/login', json={'username':'ashwin','password':'Pca12345!'})
        if resp.status_code != 200:
            print(f"Auth failed: {resp.text}")
            sys.exit(1)
        return resp.json()['access_token']
    except Exception as e:
        print(f"Auth failed: {e}")
        sys.exit(1)

def run_query(question, description=""):
    token = get_token()
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    data = {'question': question}
    
    print(f"\n--- Query: {question} ---")
    if description:
        print(f"Context: {description}")
        
    try:
        resp = requests.post('http://localhost:8000/api/v1/campaigns/chat', json=data, headers=headers)
        print(f"Status: {resp.status_code}")
        try:
           data = resp.json()
           print(f"Success: {data.get('success')}")
           if data.get('sql_query'):
               print(f"SQL: {data.get('sql_query')[:300]}...")
           if data.get('error'):
               print(f"Error: {data.get('error')}")
           if data.get('data'):
               print(f"Rows: {len(data.get('data'))}")
        except:
            print("Raw Response:", resp.text[:500])
    except Exception as e:
        print(f"Request failed: {e}")
    
    time.sleep(2)

if __name__ == "__main__":
    test_cases = [
        ("Which channels delivered the lowest cost per conversion for this campaign?", "Channel weighting for the next flight"),
        ("Did our planned channel mix align with actual performance?", "Planned spend allocation vs actual ROI"),
        ("At what spend level did performance start to plateau for each channel?", "Detecting diminishing returns curves"),
        ("Which audiences responded best, and which were over-exposed?", "Audience segment expansion and frequency control"),
        ("Which geographies over- or under-performed relative to budget allocation?", "Regional budget shifts and prioritization"),
        ("Did device allocation align with how users actually converted?", "Optimize mobile vs desktop weighting"),
        ("Which campaigns showed signs of creative or audience fatigue?", "Decline detection/Rotation trigger"),
        ("Which tactics drove upper-funnel reach vs lower-funnel conversions?", "Awareness vs Performance role separation"),
        ("What was the incremental impact of each channel on conversions?", "Contribution beyond attribution"),
        ("Based on this campaign, how should we re-plan the next flight?", "Synthesis for future building and budget split")
    ]
    
    for q, desc in test_cases:
        run_query(q, desc)
