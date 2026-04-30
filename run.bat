@echo off

echo =========================
echo 0. Installing Requirements
echo =========================
python -m pip install -r requirements.txt

echo =========================
echo 1. Starting Backend API
echo =========================
start "Backend API" cmd /k python -m uvicorn backend.app.main:app --reload --port 8000

echo =========================
echo 2. Starting Streamlit UI
echo =========================
python -m streamlit run frontend/app.py
