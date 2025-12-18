import streamlit as st
import json, os
from datetime import datetime
from uuid import uuid4

# ================= BASIC =================
st.set_page_config(page_title="AOUSE CHAT", layout="centered")

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
                "id": "admin",
                "password": "1234",
                "name": "아진이",
                "avatar": None,
                "theme": "rose"
            }
        }, f, ensure_ascii=False)

# ================= LOAD =================
messages = json.load(open(MSG_FILE, encoding="utf-8"))
users = json.load(open(USER_FILE, encoding="utf-8"))
admin = users["admin"]

# ================= SESSION =================
if "login" not in st.session_state:
    st.session_state.login = False
    st.session_state.role = "guest"

# ================= THEME =================
THEMES = {
    "rose": "#D98B8B",
    "rose_soft": "#E2A1A1"
}
THEME_COLOR = THEMES.get(admin.get("theme"), "#D98B8B")

# ================= STYLE =================
st.markdown(f"""
<style>
body {{ background:#FFF6F6; }}
* {{ font-family:'Pretendard',sans-serif; }}
.chat {{ max-width:420px; margin:auto; padding:24px 14px; }}
.date {{ margin:20px auto; padding:8px 18px; background:#EFEAEA; border-radius:999px; width:fit-content; font-size:14px; box-shadow:0 2px 6px rgba(0,0,0,0.08); }}
.msg {{ display:flex; gap:8px; margin-bottom:18px; }}
.left {{ justify-content:flex-start; }}
.right {{ justify-content:flex-end; }}
.avatar {{ width:42px; height:42px; border-radius:50%; object-fit:cover; box-shadow:0 2px 6px rgba(0,0,0,0.15); }}
.bubble {{ background:{THEME_COLOR}; color:#FFFDFD; padding:14px 18px; border-radius:18px; max-width:260px; box-shadow:0 6px 12px rgba(217,139,139,0.35); line-height:1.4; }}
.name {{ font-size:13px; opacity:0.9; margin-bottom:6px; }}
.time {{ font-size:11px; opacity:0.7; margin-top:6px; display:block; text-align:right; }}
.chat-img {{ margin-top:8px; border-radius:12px; max-width:200px; }}
</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================
st.sidebar.title("관리자")

if not st.session_state.login:
    with st.sidebar.form("login"):
        uid = st.text_input("아이디")
        pw = st.text_input("비밀번호", type="password")
        if st.form_submit_button("로그인"):
            if uid == admin["id"] and pw == admin["password"]:
                st.session_state.login = True
                st.session_state.role = "admin"
                st.rerun()
else:
    if st.sidebar.button("로그아웃"):
        st.session_state.login = False
        st.session_state.role = "guest"
        st.rerun()

# ================= ADMIN SETTINGS =================
if st.session_state.role == "admin":
    st.sidebar.subheader("프로필 설정")
    admin["name"] = st.sidebar.text_input("이름", admin["name"])
    admin["theme"] = st.sidebar.selectbox("테마", THEMES.keys(), index=list(THEMES).index(admin["theme"]))
    avatar = st.sidebar.file_uploader("프사 변경", type=["png","jpg"])

    if st.sidebar.button("저장"):
        if avatar:
            path = f"{UPLOADS}/{uuid4()}.png"
            with open(path, "wb") as f:
                f.write(avatar.read())
            admin["avatar"] = path
        users["admin"] = admin
        json.dump(users, open(USER_FILE,"w",encoding="utf-8"), ensure_ascii=False)
        st.rerun()

# ================= CHAT VIEW =================
st.markdown("<div class='chat'>", unsafe_allow_html=True)
st.markdown("<div class='date'>2025.12.18</div>", unsafe_allow_html=True)

# 답장 대상 선택 상태
if "reply_to" not in st.session_state:
    st.session_state.reply_to = None

for m in messages:
    side = "right" if m["role"] == "guest" else "left"
    st.markdown(f"<div class='msg {side}'>", unsafe_allow_html=True)

    if m["role"] == "admin" and admin.get("avatar"):
        st.markdown(f"<img class='avatar' src='{admin['avatar']}'>", unsafe_allow_html=True)

    st.markdown("<div class='bubble'>", unsafe_allow_html=True)

    # 답장 인용 표시
    if m.get("reply_to"):
        ref = next((x for x in messages if x["id"] == m["reply_to"]), None)
        if ref:
            st.markdown(f"<div style='font-size:12px;opacity:.7;margin-bottom:6px;border-left:3px solid #fff;padding-left:8px'>↪ {ref['text']}</div>", unsafe_allow_html=True)

    if m["role"] == "admin":
        st.markdown(f"<div class='name'>{admin['name']} 🎀 ✔</div>", unsafe_allow_html=True)

    st.markdown(m["text"], unsafe_allow_html=True)

    if m.get("image"):
        st.markdown(f"<img class='chat-img' src='{m['image']}'>", unsafe_allow_html=True)

    st.markdown(f"<span class='time'>{m['time']}</span>", unsafe_allow_html=True)

    # 관리자만 답장 버튼
    if st.session_state.role == "admin" and m["role"] == "guest":
        if st.button("답장", key=f"reply_{m['id']}"):
            st.session_state.reply_to = m["id"]

    st.markdown("</div></div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ================= INPUT =================
st.divider()
with st.form("send", clear_on_submit=True):
    text = st.text_input("메시지")
    img = st.file_uploader("사진", type=["png","jpg"], label_visibility="collapsed")
    if st.form_submit_button("보내기") and text:
        path = None
        if img:
            path = f"{UPLOADS}/{uuid4()}.png"
            with open(path, "wb") as f:
                f.write(img.read())
        messages.append({
            "id": str(uuid4()),
            "role": st.session_state.role,
            "text": text,
            "image": path,
            "time": datetime.now().strftime("%H:%M")
        })
        json.dump(messages, open(MSG_FILE,"w",encoding="utf-8"), ensure_ascii=False)
        st.rerun()

