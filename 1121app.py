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
with open(MSG_FILE, encoding="utf-8") as f:
    messages = json.load(f)
with open(USER_FILE, encoding="utf-8") as f:
    users = json.load(f)

admin = users.get("admin", {})

# ================= SESSION =================
if "login" not in st.session_state:
    st.session_state.login = False
if "role" not in st.session_state:
    st.session_state.role = "guest"
if "reply_to" not in st.session_state:
    st.session_state.reply_to = None

# ================= THEME =================
THEMES = {
    "rose": "#D98B8B",
    "rose_soft": "#E2A1A1"
}
THEME_COLOR = THEMES.get(admin.get("theme", "rose"), "#D98B8B")

# ================= STYLE =================
st.markdown(f"""
<style>
body { background:#FFF6F6; }
* { font-family:'Pretendard',sans-serif; box-sizing:border-box; }

/* ===== MOBILE FIRST ===== */
.chat {
  max-width: 420px;
  margin: 0 auto;
  padding: 20px 12px 120px;
}

/* PC에서는 모바일 화면처럼 */
@media (min-width: 768px) {
  .chat {
    max-width: 390px;
  }
}

.date {
  margin: 18px auto;
  padding: 8px 18px;
  background:#EFEAEA;
  border-radius:999px;
  width:fit-content;
  font-size:13px;
  color:#555;
  box-shadow:0 2px 6px rgba(0,0,0,0.08);
}

.msg { display:flex; gap:8px; margin-bottom:16px; }
.left { justify-content:flex-start; }
.right { justify-content:flex-end; }

.avatar {
  width:40px;
  height:40px;
  border-radius:50%;
  object-fit:cover;
  box-shadow:0 2px 6px rgba(0,0,0,0.15);
}

.bubble {
  background:#D98B8B;
  color:#FFFDFD;
  padding:14px 18px;
  border-radius:18px;
  max-width:72%;
  box-shadow:0 6px 12px rgba(217,139,139,0.35);
  line-height:1.5;
  letter-spacing:-0.2px;
}

.left .bubble {
  box-shadow:0 6px 14px rgba(217,139,139,0.45);
}

.right .bubble {
  box-shadow:0 4px 10px rgba(217,139,139,0.25);
}

.name {
  font-size:12px;
  font-weight:500;
  opacity:0.85;
  margin-bottom:4px;
}

.text {
  font-size:14.5px;
  font-weight:400;
}

.time {
  font-size:11px;
  opacity:0.65;
  margin-top:6px;
  display:block;
  text-align:right;
}

.chat-img {
  margin-top:8px;
  border-radius:12px;
  max-width:200px;
}

.reply-quote {
  font-size:12px;
  opacity:0.6;
  margin-bottom:8px;
  border-left:2px solid rgba(255,255,255,0.6);
  padding-left:8px;
}

.replying {
  font-size:13px;
  opacity:0.75;
  margin-bottom:8px;
}

/* 입력창 모바일 고정 느낌 */
section[data-testid="stForm"] {
  position:fixed;
  bottom:0;
  left:50%;
  transform:translateX(-50%);
  width:100%;
  max-width:420px;
  background:#FFF6F6;
  padding:10px 12px 14px;
  border-top:1px solid rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================
st.sidebar.title("관리자")

if not st.session_state.login:
    with st.sidebar.form("login_form"):
        uid = st.text_input("아이디")
        pw = st.text_input("비밀번호", type="password")
        if st.form_submit_button("로그인"):
            if uid == admin.get("id") and pw == admin.get("password"):
                st.session_state.login = True
                st.session_state.role = "admin"
                st.rerun()
else:
    if st.sidebar.button("로그아웃"):
        st.session_state.login = False
        st.session_state.role = "guest"
        st.session_state.reply_to = None
        st.rerun()

# ================= ADMIN SETTINGS =================
if st.session_state.role == "admin":
    st.sidebar.subheader("프로필 설정")
    admin["name"] = st.sidebar.text_input("이름", admin.get("name", ""))
    admin["theme"] = st.sidebar.selectbox("테마", list(THEMES.keys()), index=list(THEMES.keys()).index(admin.get("theme", "rose")))
    avatar = st.sidebar.file_uploader("프사 변경", type=["png","jpg"])

    if st.sidebar.button("저장"):
        if avatar:
            path = f"{UPLOADS}/{uuid4()}.png"
            with open(path, "wb") as f:
                f.write(avatar.read())
            admin["avatar"] = path
        users["admin"] = admin
        with open(USER_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False)
        st.rerun()

# ================= CHAT VIEW =================
st.markdown("<div class='chat'>", unsafe_allow_html=True)
st.markdown("<div class='date'>2025.12.18</div>", unsafe_allow_html=True)

for m in messages:
    side = "right" if m.get("role") == "guest" else "left"
    st.markdown(f"<div class='msg {side}'>", unsafe_allow_html=True)

    if m.get("role") == "admin" and admin.get("avatar"):
        st.markdown(f"<img class='avatar' src='{admin['avatar']}'>", unsafe_allow_html=True)

    st.markdown("<div class='bubble'>", unsafe_allow_html=True)

    if m.get("reply_to"):
        ref = next((x for x in messages if x.get("id") == m.get("reply_to")), None)
        if ref:
            st.markdown(f"<div class='reply-quote'>↪ {ref.get('text','')}</div>", unsafe_allow_html=True)

    if m.get("role") == "admin":
        st.markdown(f"<div class='name'>{admin.get('name','')} 🎀 ✔</div>", unsafe_allow_html=True)

    st.markdown(m.get("text",""), unsafe_allow_html=True)

    if m.get("image"):
        st.markdown(f"<img class='chat-img' src='{m['image']}'>", unsafe_allow_html=True)

    st.markdown(f"<span class='time'>{m.get('time','')}</span>", unsafe_allow_html=True)

    if st.session_state.role == "admin" and m.get("role") == "guest":
        if st.button("답장", key=f"reply_{m['id']}"):
            st.session_state.reply_to = m['id']

    st.markdown("</div></div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ================= INPUT =================
st.divider()

if st.session_state.reply_to:
    ref = next((x for x in messages if x.get("id") == st.session_state.reply_to), None)
    if ref:
        st.markdown(f"<div class='replying'>↪ 답장 중: {ref.get('text','')}</div>", unsafe_allow_html=True)
        if st.button("답장 취소"):
            st.session_state.reply_to = None
            st.rerun()

with st.form("send_form", clear_on_submit=True):
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
            "reply_to": st.session_state.reply_to,
            "time": datetime.now().strftime("%H:%M")
        })
        with open(MSG_FILE, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False)
        st.session_state.reply_to = None
        st.rerun()
