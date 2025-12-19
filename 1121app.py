import streamlit as st
import os, json
from datetime import datetime
from PIL import Image

# ================= 설정 =================
st.set_page_config(page_title="Chat", layout="centered")

DATA = "data"
MSG_FILE = f"{DATA}/messages.json"
ADMIN_FILE = f"{DATA}/admin.json"
AVATAR_DIR = f"{DATA}/avatars"
os.makedirs(DATA, exist_ok=True)
os.makedirs(AVATAR_DIR, exist_ok=True)

# ================= 관리자 =================
def load_admin():
    if not os.path.exists(ADMIN_FILE):
        admin = {
            "id": "admin",
            "pw": "1234",
            "name": "관리자",
            "avatar": None
        }
        json.dump(admin, open(ADMIN_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return json.load(open(ADMIN_FILE, "r", encoding="utf-8"))

def save_admin(a):
    json.dump(a, open(ADMIN_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

admin = load_admin()

# ================= 메시지 =================
def load_msgs():
    if not os.path.exists(MSG_FILE):
        return []
    return json.load(open(MSG_FILE, "r", encoding="utf-8"))

def save_msgs(m):
    json.dump(m, open(MSG_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

# ================= 세션 =================
if "login" not in st.session_state:
    st.session_state.login = False
if "reply" not in st.session_state:
    st.session_state.reply = None

# ================= 스타일 =================
st.markdown("""
<style>
body { background:#FFEFF4; }
.chat {
  max-width:390px;
  margin:auto;
  padding:20px 12px 160px;
}

.msg { display:flex; margin-bottom:18px; }
.left { justify-content:flex-start; }
.right { justify-content:flex-end; }

.avatar {
  width:40px; height:40px;
  border-radius:50%;
  margin-right:8px;
  object-fit:cover;
}

.bubble {
  padding:14px 16px;
  border-radius:18px;
  max-width:72%;
  font-size:14px;
  line-height:1.5;
}

.q { background:#FFFFFF; color:#333; }
.a { background:#F6A5C0; color:#FFFFFF; }

.reply {
  font-size:12px;
  opacity:.75;
  margin-bottom:6px;
  border-left:3px solid rgba(255,255,255,.7);
  padding-left:8px;
}

.time {
  font-size:11px;
  opacity:.6;
  margin-top:6px;
  text-align:right;
}

.chat-img {
  max-width:100%;
  border-radius:12px;
  margin-top:6px;
}

section[data-testid="stForm"] {
  position:fixed;
  bottom:0; left:50%;
  transform:translateX(-50%);
  width:100%;
  max-width:390px;
  background:#FFEFF4;
  padding:10px;
  border-top:1px solid rgba(0,0,0,.05);
}
</style>
""", unsafe_allow_html=True)

# ================= 사이드바 =================
with st.sidebar:
    if not st.session_state.login:
        uid = st.text_input("ID")
        pw = st.text_input("PW", type="password")
        if st.button("로그인"):
            if uid == admin["id"] and pw == admin["pw"]:
                st.session_state.login = True
                st.rerun()
            else:
                st.error("로그인 실패")
    else:
        st.success("관리자 로그인")
        admin["name"] = st.text_input("이름", admin["name"])

        avatar = st.file_uploader("프사 업로드", type=["png", "jpg", "jpeg"])
        if avatar:
            img = Image.open(avatar)
            path = f"{AVATAR_DIR}/avatar.png"
            img.save(path)
            admin["avatar"] = path

        save_admin(admin)

        if st.button("로그아웃"):
            st.session_state.login = False
            st.session_state.reply = None
            st.rerun()

# ================= 채팅 =================
msgs = load_msgs()
st.markdown("<div class='chat'>", unsafe_allow_html=True)

for i, m in enumerate(msgs):
    # 🔒 핵심: 절대 KeyError 안 나게
    t = m.get("type", "question")

    # 🔒 질문은 무조건 오른쪽 / 답변은 무조건 왼쪽
    side = "right" if t == "question" else "left"
    bubble = "q" if t == "question" else "a"

    st.markdown(f"<div class='msg {side}'>", unsafe_allow_html=True)

    if side == "left" and admin.get("avatar"):
        st.markdown(f"<img src='{admin['avatar']}' class='avatar'>", unsafe_allow_html=True)

    st.markdown(f"<div class='bubble {bubble}'>", unsafe_allow_html=True)

    # ✅ 답장 질문은 말풍선 안에만
    if m.get("reply"):
        st.markdown(f"<div class='reply'>↪ {m['reply']}</div>", unsafe_allow_html=True)

    if m.get("text"):
        st.markdown(m["text"], unsafe_allow_html=True)

    if m.get("image"):
        st.markdown(f"<img src='{m['image']}' class='chat-img'>", unsafe_allow_html=True)

    st.markdown(f"<div class='time'>{m.get('time','')}</div>", unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

    if t == "question" and st.session_state.login:
        if st.button("답장", key=f"r{i}"):
            st.session_state.reply = m.get("text")
            st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# ================= 입력 =================
with st.form("send", clear_on_submit=True):
    if st.session_state.reply:
        st.markdown(f"↪ 답장 중: {st.session_state.reply}")

    txt = st.text_input("메시지")
    img = st.file_uploader("사진", type=["png", "jpg", "jpeg"])
    send = st.form_submit_button("보내기")

if send and (txt or img):
    img_path = None
    if img:
        path = f"{DATA}/{datetime.now().timestamp()}_{img.name}"
        Image.open(img).save(path)
        img_path = path

    msgs.append({
        "type": "answer" if st.session_state.login and st.session_state.reply else "question",
        "text": txt,
        "image": img_path,
        "reply": st.session_state.reply,
        "time": datetime.now().strftime("%H:%M")
    })
    save_msgs(msgs)
    st.session_state.reply = None
    st.rerun()
