import streamlit as st
from collections import deque
import requests
import threading

from api_client import signup, login, google_login, get_history, translate, delete_history_item

st.set_page_config(page_title="Oui Oui Dịch Việt-Pháp", page_icon="🥐", layout="wide")

WELCOME = {"content": "Oui Oui Dịch Việt-Pháp"}

if "user" not in st.session_state:
    st.session_state.user = None

if "messages" not in st.session_state:
    st.session_state.messages = deque([WELCOME], maxlen=8)

if "show_signup" not in st.session_state:
    st.session_state.show_signup = False

if "show_login" not in st.session_state:
    st.session_state.show_login = True

if "translation_output" not in st.session_state:
    st.session_state.translation_output = ""

if "source_text_input" not in st.session_state:
    st.session_state.source_text_input = ""


def load_history():
    if not st.session_state.user:
        return
    try:
        msgs = get_history(st.session_state.user["idToken"], limit=8)
        st.session_state.messages = deque(msgs, maxlen=8)
    except Exception:
        st.session_state.messages = deque([WELCOME], maxlen=8)


def clear_google_query_params():
    try:
        st.query_params.clear()
    except Exception:
        pass

def select_history(source, target):
    st.session_state["main_text_area"] = source
    st.session_state.translation_output = target
    st.session_state.source_text_input = source


def handle_google_login_callback():
    if st.session_state.user:
        return

    params = st.query_params
    raw_token = params.get("id_token")

    if not raw_token:
        return

    id_token = raw_token[0] if isinstance(raw_token, list) else raw_token

    try:
        user = google_login(id_token)
        st.session_state.user = user
        load_history()
        clear_google_query_params()
        st.success("Đăng nhập Google thành công")
        st.rerun()
    except requests.HTTPError as e:
        st.error(f"Đăng nhập Google thất bại: {e}")
        clear_google_query_params()
    except Exception as e:
        st.error(f"Lỗi xử lý Google login: {e}")
        clear_google_query_params()


def login_form():
    st.subheader("Đăng nhập")

    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Mật khẩu", type="password")
        submitted = st.form_submit_button("Đăng nhập")
        goto_signup = st.form_submit_button("Chưa có tài khoản? Đăng ký")

    if goto_signup:
        st.session_state.show_signup = True
        st.session_state.show_login = False
        st.rerun()

    if submitted:
        try:
            user = login(email, password)
            st.session_state.user = user
            load_history()
            st.success("Đăng nhập thành công")
            st.rerun()
        except requests.HTTPError as e:
            try:
                error_detail = e.response.json().get("detail", str(e))
            except Exception:
                error_detail = str(e)
            st.error(f"Đăng nhập thất bại: {error_detail}")
        except Exception as e:
            st.error(f"Lỗi đăng nhập: {e}")

    st.markdown("### Hoặc")

    google_login_url = dict(st.secrets["google-login"])["google-url"]

    if google_login_url:
        st.markdown(
        f'''
        <a href="{google_login_url}" target="_self" style="
            display: inline-block;
            width: 100%;
            text-align: center;
            padding: 0.6rem 1rem;
            background-color: white;
            color: black;
            text-decoration: none;
            border-radius: 0.5rem;
            border: 1px solid #ddd;
            font-weight: 600;
        ">
            Đăng nhập với Google
        </a>
        ''',
        unsafe_allow_html=True,
    )
    else:
        st.info(
            "Chưa cấu hình Google-login trong secrets. "
            "Hãy thêm URL đăng nhập Google để dùng tính năng này."
        )


def signup_form():
    st.subheader("Đăng ký")
    with st.form("signup_form"):
        email = st.text_input("Email")
        password = st.text_input("Mật khẩu", type="password")
        submitted = st.form_submit_button("Tạo tài khoản")
        goto_login = st.form_submit_button("Đã có tài khoản? Đăng nhập")

    if goto_login:
        st.session_state.show_signup = False
        st.session_state.show_login = True
        st.rerun()

    if submitted:
        try:
            signup(email, password)
            st.success("Tạo tài khoản thành công, hãy đăng nhập")
            st.session_state.show_signup = False
            st.session_state.show_login = True
            st.rerun()
        except requests.HTTPError as e:
            try:
                error_detail = e.response.json().get("detail", str(e))
            except Exception:
                error_detail = str(e)
            st.error(f"Đăng ký thất bại: {error_detail}")
        except Exception as e:
            st.error(f"Lỗi đăng ký: {e}")


handle_google_login_callback()

st.title("Oui Oui Dịch Việt-Pháp")

if st.session_state.user:
    st.sidebar.success(f"Đang đăng nhập: {st.session_state.user['email']}")
    if st.sidebar.button("Đăng xuất"):
        st.session_state.user = None
        st.session_state.messages = deque([WELCOME], maxlen=8)
        clear_google_query_params()
        st.rerun()
else:
    if st.session_state.show_signup:
        signup_form()
    else:
        login_form()

st.divider()

if st.session_state.user:
    source_text = st.text_area(
        "Source Text", 
        placeholder="Điền văn bản vào đây...", 
        height=150,
        key="main_text_area"
    )
    
    if st.button("Dịch sang tiếng Pháp"):
        if source_text:
            st.session_state.source_text_input = source_text
            try:
                res = translate(st.session_state.user["idToken"], source_text)
                st.session_state.translation_output = res.get("text", "")
                
                st.session_state.messages.appendleft({"content": source_text})
                st.session_state.messages.appendleft({"content": st.session_state.translation_output})
            except Exception as e:
                st.session_state.translation_output = f"Translation Error: {e}"
            st.rerun()

    st.divider()

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Kết quả dịch sang tiếng Pháp")
        st.info(st.session_state.translation_output if st.session_state.translation_output else "Kết quả dịch ở đây...")

    with col2:
        st.subheader("Lịch sử dịch gần đây")
        
        history_list = list(st.session_state.messages)
        actual_msgs = [m for m in history_list if m != WELCOME]
        
        if actual_msgs:
            pairs = []
            for i in range(0, len(actual_msgs), 2):
                if i + 1 < len(actual_msgs):
                    pairs.append((actual_msgs[i+1], actual_msgs[i]))
            
            for idx, (source_msg, target_msg) in enumerate(pairs):
                h_col1, h_col2 = st.columns([0.85, 0.15])
                
                source_content = source_msg["content"]
                target_content = target_msg["content"]
                btn_label = f"📝 {source_content[:20]}..." if len(source_content) > 20 else f"📝 {source_content}"
                
                with h_col1:
                    if st.button(
                        btn_label, 
                        key=f"hist_btn_{idx}", 
                        use_container_width=True,
                        on_click=select_history,
                        args=(source_content, target_content)
                    ):
                        pass
                
                with h_col2:
                    if st.button("❌", key=f"del_btn_{idx}", help="Xóa mục này"):
                        st.session_state.messages = deque(
                            [m for m in st.session_state.messages if m["content"] not in [source_content, target_content]], 
                            maxlen=8
                    )
                        
                        def background_delete(c1, c2, token):
                            try:
                                delete_history_item(token, c1)
                                delete_history_item(token, c2)
                            except Exception:
                                pass
                        
                        threading.Thread(
                            target=background_delete, 
                            args=(source_content, target_content, st.session_state.user["idToken"])
                        ).start()
                        
                        st.rerun()
        else:
            st.caption("Chưa có lịch sử dịch.")
