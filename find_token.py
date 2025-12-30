import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = "http://localhost:8000/api/v1"

def login(username, password):
    print(f"尝试登录用户: {username}...")
    try:
        response = requests.post(f"{API_URL}/auth/login", json={
            "username": username,
            "password": password
        })
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"✅ 登录成功! Token: {token[:20]}...")
            return token
        else:
            print(f"❌ 登录失败: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None

if __name__ == "__main__":
    # 尝试一些常见的默认密码
    for pwd in ["admin123", "password", "Admin123", "ashwin123"]:
        token = login("admin", pwd)
        if token:
            print(f"\n找到密码: {pwd}")
            print(f"DEBUG_AUTH_TOKEN={token}")
            break
        
        token = login("ashwin", pwd)
        if token:
            print(f"\n找到密码: {pwd}")
            print(f"DEBUG_AUTH_TOKEN={token}")
            break
