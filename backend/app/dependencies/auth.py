from fastapi import Header, HTTPException
from firebase_admin import auth as admin_auth
from backend.app.core.firebase_config import init_firebase_admin

def get_current_user(authorization: str = Header(...)):
    init_firebase_admin()

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.replace("Bearer ", "").strip()

    try:
        decoded = admin_auth.verify_id_token(token)
        return {
            "uid": decoded.get("uid"),
            "email": decoded.get("email"),
            "token": token
        }
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")