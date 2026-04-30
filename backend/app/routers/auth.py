import os
import secrets
from urllib.parse import urlencode

import requests
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from firebase_admin import auth as admin_auth

from backend.app.schemas.auth import (
    SignupRequest, LoginRequest, GoogleLoginRequest
)
from backend.app.core.firebase_config import get_pyrebase_auth, init_firebase_admin
from backend.app.dependencies.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

auth_client = get_pyrebase_auth()
init_firebase_admin()


import streamlit as st

google_cfg = st.secrets["google-login"]

GOOGLE_URL = google_cfg["google-url"]
GOOGLE_CLIENT_ID = google_cfg["google_client_id"]
GOOGLE_CLIENT_SECRET = google_cfg["google_client_secret"]
GOOGLE_REDIRECT_URI = google_cfg["google_redirect_uri"]
FIREBASE_WEB_API_KEY = google_cfg["firebase_web_api_key"]
FRONTEND_URL = google_cfg["frontend_url"]
COOKIE_SECURE = google_cfg["cookie_secure"]


@router.post("/signup")
def signup(payload: SignupRequest):
    try:
        auth_client.create_user_with_email_and_password(payload.email, payload.password)
        return {"message": "Tạo tài khoản thành công"}
    except Exception as e:
        error_msg = str(e)
        if "EMAIL_EXISTS" in error_msg:
            detail = "Email này đã được đăng ký. Nếu bạn từng dùng Google Login, hãy tiếp tục dùng Google Login."
        elif "OPERATION_NOT_ALLOWED" in error_msg or "PASSWORD_LOGIN_DISABLED" in error_msg:
            detail = "Tính năng Đăng nhập bằng Email/Mật khẩu chưa được bật trong Firebase Console."
        else:
            detail = f"Lỗi đăng ký: {error_msg}"
        raise HTTPException(status_code=400, detail=detail)


@router.post("/login")
def login(payload: LoginRequest):
    try:
        user = auth_client.sign_in_with_email_and_password(payload.email, payload.password)
        return {
            "email": payload.email,
            "uid": user["localId"],
            "idToken": user["idToken"],
            "refreshToken": user.get("refreshToken")
        }
    except Exception as e:
        error_msg = str(e)
        if "EMAIL_NOT_FOUND" in error_msg or "INVALID_LOGIN_CREDENTIALS" in error_msg:
            detail = "Email hoặc mật khẩu không chính xác."
        elif "INVALID_PASSWORD" in error_msg:
            detail = "Mật khẩu không chính xác."
        elif "PASSWORD_LOGIN_DISABLED" in error_msg:
            detail = "Tính năng Đăng nhập bằng Email chưa được bật trong Firebase."
        else:
            detail = f"Lỗi xác thực: {error_msg}"
        raise HTTPException(status_code=401, detail=detail)


@router.post("/google")
def google_login(payload: GoogleLoginRequest):
    try:
        decoded = admin_auth.verify_id_token(payload.id_token)
        return {
            "email": decoded.get("email"),
            "uid": decoded.get("uid"),
            "idToken": payload.id_token
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Google token invalid: {e}")


@router.get("/google/start")
def google_start():
    state = secrets.token_urlsafe(32)

    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "select_account",
    }

    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        + urlencode(params)
    )

    response = RedirectResponse(url=google_auth_url, status_code=302)
    response.set_cookie(
        key="google_oauth_state",
        value=state,
        max_age=600,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="lax",
        path="/",
    )
    return response


@router.get("/google/callback")
def google_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
):
    if error:
        raise HTTPException(status_code=400, detail=f"Google OAuth error: {error}")

    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    saved_state = request.cookies.get("google_oauth_state")
    if not saved_state or not state or saved_state != state:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")

    token_resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        },
        timeout=20,
    )

    if not token_resp.ok:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to exchange Google code: {token_resp.text}"
        )

    token_data = token_resp.json()
    google_id_token = token_data.get("id_token")

    if not google_id_token:
        raise HTTPException(status_code=400, detail="Google did not return id_token")

    firebase_resp = requests.post(
        f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key={FIREBASE_WEB_API_KEY}",
        json={
            "postBody": urlencode({
                "id_token": google_id_token,
                "providerId": "google.com",
            }),
            "requestUri": GOOGLE_REDIRECT_URI,
            "returnIdpCredential": True,
            "returnSecureToken": True,
        },
        timeout=20,
    )

    if not firebase_resp.ok:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to sign in with Firebase Google provider: {firebase_resp.text}"
        )

    firebase_data = firebase_resp.json()
    firebase_id_token = firebase_data.get("idToken")

    if not firebase_id_token:
        raise HTTPException(status_code=400, detail="Firebase did not return idToken")

    separator = "&" if "?" in FRONTEND_URL else "?"
    redirect_to_frontend = f"{FRONTEND_URL}{separator}{urlencode({'id_token': firebase_id_token})}"

    response = RedirectResponse(url=redirect_to_frontend, status_code=302)
    response.delete_cookie("google_oauth_state", path="/")
    return response


@router.get("/me")
def me(user=Depends(get_current_user)):
    return {
        "email": user["email"],
        "uid": user["uid"]
    }