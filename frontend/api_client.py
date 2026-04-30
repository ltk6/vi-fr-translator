import requests

API_BASE = "http://localhost:8000"

def signup(email: str, password: str):
    r = requests.post(f"{API_BASE}/auth/signup", json={
        "email": email,
        "password": password
    })
    r.raise_for_status()
    return r.json()

def login(email: str, password: str):
    r = requests.post(f"{API_BASE}/auth/login", json={
        "email": email,
        "password": password
    })
    r.raise_for_status()
    return r.json()

def google_login(id_token: str):
    r = requests.post(f"{API_BASE}/auth/google", json={
        "id_token": id_token
    })
    r.raise_for_status()
    return r.json()

def get_history(id_token: str, limit: int = 8):
    r = requests.get(
        f"{API_BASE}/translate/history",
        params={"limit": limit},
        headers={"Authorization": f"Bearer {id_token}"}
    )
    r.raise_for_status()
    return r.json()

def translate(id_token: str, text: str):
    r = requests.post(
        f"{API_BASE}/translate",
        json={"text": text},
        headers={"Authorization": f"Bearer {id_token}"}
    )
    r.raise_for_status()
    return r.json()

def delete_history_item(id_token: str, content: str):
    r = requests.delete(
        f"{API_BASE}/translate/delete",
        json={"text": content},
        headers={"Authorization": f"Bearer {id_token}"}
    )
    r.raise_for_status()
    return r.json()