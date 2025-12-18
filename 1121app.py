import streamlit as st
import json, os
from datetime import datetime
from uuid import uuid4

# ================= BASIC =================
st.set_page_config(page_title="Chat", layout="centered")

DATA = "data"
MSG_FILE = f"{DATA}/messages.json"
USER_FILE = f"{DATA}/users.json"
UPLOADS = "uploads"

os.makedirs(DATA, exist_ok=True)
os.makedirs(UPLOADS, exist_ok=True)

# ================= INIT FILES =================
if not os.path.exists(MSG_FILE):
    with open(MSG_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False)

if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "admin": {
                "password": "1234",
                "name": "아진이",
                "avatar": None,
                "theme": "rose"
            }
        }, f, ensure_ascii=False)

# ================= LOAD =================
messages = json.load(open(MSG_FILE, encoding="utf-8"))
users = json.load(open(USER_FILE, encoding="utf-8"))

# ================= SESSION =================
if "login" not in st.session_state:
    st.session_state.login = False
    st.session_state.user = "guest"

# ================= THEMES =================
THEMES = {
    "rose": "#D98B8B",
    "soft": "#E6A6A6"
}

admin = users.get("admin")
THEME_COLOR = THEMES.get(admin.get("theme"), "#D98B8B")

# ================= STYLE =================
st.markdown(f"""
<style>
body {{ background:#FFF6F6; }}
.chat {{ max-width:420px; margin:auto; }}
.date {{ margin:20px auto; padding:6px 16px; background:#EFEAEA; border-radius:999px; width:fit-content; font-size:14px; }}
.msg {{ display:flex; margin-bottom:16px; }}
.left {{ justify-content:flex-start; }}
.right {{ justify-content:flex-end; }}
.avatar {{ width:40px; height:40px; border-radius:50%; margin-right:8px; object-fit:cover; }}
.bubble {{ background:{THEME_COLOR}; color:white; padding:14px 18px; border-radius:18px; max-width:260px; box-shadow:0 6px 12px rgba(0,0,0,0.15); }}
.name {{ font-size:13px; opacity:0.9; margin-bottom:6px; }}
.time {{ font-size:11px; opacity:0.7; margin-top:6px; display:block; }}
img.chat-img {{ margin-top:8px; border-radius:12px; max-width:200px; }}
</style>
""", unsafe_allow_html=True)

# ================= LOGIN =================
st.sidebar.title("설정")

if not st.session_state.login:
    if st.sidebar.button("관리자 로그인"):
        st.session_state.login = True
        st.session_state.user = "admin"
else:
    if st.sidebar.button("로그아웃"):
        st.session_state.login = False
        st.session_state.user = "guest"

# ================= ADMIN SETTINGS =================
if st.session_state.login:
    st.sidebar.subheader("프로필 설정")
    new_name = st.sidebar.text_input("이름", admin["name"])
    theme = st.sidebar.selectbox("테마", THEMES.keys())
    avatar = st.sidebar.file_uploader("프사 변경", type=["png","jpg"])

    if st.sidebar.button("저장"):
        admin["name"] = new_name
        admin["theme"] = theme
        if avatar:
            path = f"{UPLOADS}/{uuid4()}.png"
            with open(path, "wb") as f:
                f.write(avatar.read())
            admin["avatar"] = path
        users["admin"] = admin
        json.dump(users, open(USER_FILE,"w",encoding="utf-8"), ensure_ascii=False)
        st.experimental_rerun()

# ================= CHAT VIEW =================
st.markdown("<div class='chat'>", unsafe_allow_html=True)
st.markdown("<div class='date'>2025.12.18</div>", unsafe_allow_html=True)

for m in messages:
    side = "right" if m["role"] == "guest" else "left"
    st.markdown(f"<div class='msg {side}'>", unsafe_allow_html=True)

    if m["role"] == "admin" and admin.get("avatar"):
        st.markdown(f"<img class='avatar' src='{admin['avatar']}'>", unsafe_allow_html=True)

    st.markdown("<div class='bubble'>", unsafe_allow_html=True)
    if m["role"] == "admin":
        st.markdown(f"<div class='name'>{admin['name']} 🎀</div>", unsafe_allow_html=True)
    st.markdown(m["text"], unsafe_allow_html=True)

    if m.get("image"):
        st.markdown(f"<img class='chat-img' src='{m['image']}'>", unsafe_allow_html=True)

    st.markdown(f"<span class='time'>{m['time']}</span>", unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ================= INPUT =================
st.divider()
text = st.text_input("메시지")
img = st.file_uploader("사진", type=["png","jpg"], label_visibility="collapsed")

if st.button("보내기") and text:
    path = None
    if img:
        path = f"{UPLOADS}/{uuid4()}.png"
        with open(path, "wb") as f:
            f.write(img.read())

    messages.append({
        "id": str(uuid4()),
        "role": st.session_state.user,
        "text": text,
        "image": path,
        "time": datetime.now().strftime("%H:%M")
    })
    json.dump(messages, open(MSG_FILE,"w",encoding="utf-8"), ensure_ascii=False)
    st.experimental_rerun()
