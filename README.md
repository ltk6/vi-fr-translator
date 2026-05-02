# Oui Oui Dịch Việt-Pháp

Ứng dụng web dịch thuật Việt-Pháp sử dụng Hugging Face Transformers, Streamlit, FastAPI và Firebase.

## 1. Thông tin sinh viên

* Họ tên: Lâm Tuấn Khanh
* MSSV: 24120337
* Trường: Đại học Khoa Học Tự Nhiên TP.HCM
* Khoa: Công Nghệ Thông Tin

## 2. Hướng dẫn cài đặt environment

### 2.1. Clone project
```bash
git clone https://github.com/ltk6/vi-fr-translator
cd vi-fr-translator
```

### 2.2. Cài đặt thư viện
```bash
python -m pip install -r requirements.txt
```

## 3. Hướng dẫn chạy frontend
```bash
python -m streamlit run frontend/app.py
```

## 4. Hướng dẫn chạy backend
```bash
python -m uvicorn backend.app.main:app --reload --port 8000
```

## 5. Đường dẫn đến video demo
* Link: https://drive.google.com/file/d/1WY_xq2wIspha0iiKED9yCq0w_gPVT_Xk/view?usp=sharing
