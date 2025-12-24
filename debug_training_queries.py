
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
        ("What media variables are the primary drivers of conversion performance?", "Impact of levers vs tactics"),
        ("How much performance lift came from higher media investment versus better media efficiency?", "Scaling gains vs Optimization gains"),
        ("Where do we observe media saturation and diminishing returns?", "Point of declining incremental conversions"),
        ("How consistent is media performance across the campaign flight?", "KPI volatility over time"),
        ("Which media segments systematically over- or under-perform benchmarks?", "Structural inefficiencies vs opportunities"),
        ("How does each channel contribute across the media funnel?", "Awareness vs Performance role quantification"),
        ("What is the incremental impact of each media channel or tactic?", "True lift beyond attribution"),
        ("How sensitive is overall performance to changes in media budget allocation?", "Budget shift risk/upside analysis"),
        ("Which media performance signals are statistically meaningful versus noise?", "False optimization prevention"),
        ("How can we forecast media performance for future campaigns or flights?", "Predictive modeling support")
    ]
    
    for q, desc in test_cases:
        run_query(q, desc)
