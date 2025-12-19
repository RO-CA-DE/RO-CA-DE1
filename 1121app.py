import streamlit as st
import json, os
from datetime import datetime

st.set_page_config(page_title="Chat", layout="centered")

DATA = "data"
MSG = f"{DATA}/messages.json"
ADMIN = f"{DATA}/admin.json"
os.makedirs(DATA, exist_ok=True)

# ---------- 관리자 ----------
def load_admin():
    if not os.path.exists(ADMIN):
        admin = {
            "id": "admin",
            "pw": "1234",
            "name": "관리자",
            "avatar": "https://i.imgur.com/OVC5X8N.png",
            "theme": "#F3A5B5"
        }
        json.dump(admin, open(ADMIN,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
    return json.load(open(ADMIN,"r",encoding="utf-8"))

admin = load_admin()

# ---------- 메시지 ----------
def load_msgs():
    if not os.path.exists(MSG): return []
    return json.load(open(MSG,"r",encoding="utf-8"))

def save_msgs(m): json.dump(m, open(MSG,"w",encoding="utf-8"), ensure_ascii=False, indent=2)

# ---------- 세션 ----------
if "login" not in st.session_state: st.session_state.login = False
if "reply" not in st.session_state: st.session_state.reply = None

# ---------- 스타일 ----------
st.markdown(f"""
<style>
body {{ background:#FFF6F8; }}
.chat {{ max-width:390px; margin:auto; padding:20px 12px 140px; }}
.msg {{ display:flex; margin-bottom:18px; }}
.left {{ justify-content:flex-start; }}
.right {{ justify-content:flex-end; }}

.avatar {{ width:38px; height:38px; border-radius:50%; margin-right:8px; }}

.bubble {{
  background:{admin['theme']};
  color:white;
  padding:14px 16px;
  border-radius:18px;
  max-width:72%;
  font-size:14px;
}}

.reply {{
  background:rgba(255,255,255,.25);
  padding:8px 10px;
  border-radius:10px;
  font-size:12px;
  margin-bottom:8px;
}}

.time {{ font-size:11px; opacity:.6; text-align:right; margin-top:6px; }}

section[data-testid="stForm"] {{
  position:fixed; bottom:0; left:50%;
  transform:translateX(-50%);
  max-width:390px; width:100%;
  background:#FFF6F8;
  padding:10px;
}}
</style>
""", unsafe_allow_html=True)

# ---------- 사이드바 ----------
with st.sidebar:
    if not st.session_state.login:
        i = st.text_input("ID")
        p = st.text_input("PW", type="password")
        if st.button("로그인") and i==admin["id"] and p==admin["pw"]:
            st.session_state.login=True; st.rerun()
    else:
        admin["name"] = st.text_input("이름", admin["name"])
        admin["avatar"] = st.text_input("프사 URL", admin["avatar"])
        admin["theme"] = st.color_picker("테마", admin["theme"])
        json.dump(admin, open(ADMIN,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
        if st.button("로그아웃"):
            st.session_state.login=False; st.session_state.reply=None; st.rerun()

# ---------- 채팅 ----------
msgs = load_msgs()
st.markdown("<div class='chat'>", unsafe_allow_html=True)

for idx,m in enumerate(msgs):
    t = m.get("type","question")
    side = "right" if t=="question" else "left"

    st.markdown(f"<div class='msg {side}'>", unsafe_allow_html=True)

    if side=="left":
        st.markdown(f"<img class='avatar' src='{admin['avatar']}'>", unsafe_allow_html=True)

    st.markdown("<div class='bubble'>", unsafe_allow_html=True)

    # 🔥 답장 인용은 말풍선 안으로
    if m.get("reply"):
        st.markdown(f"<div class='reply'>↪ {m['reply']}</div>", unsafe_allow_html=True)

    st.markdown(m["text"], unsafe_allow_html=True)
    st.markdown(f"<div class='time'>{m['time'][-5:]}</div>", unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

    if t=="question" and st.session_state.login:
        if st.button("답장", key=idx):
            st.session_state.reply = m["text"]; st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# ---------- 입력 ----------
with st.form("send", clear_on_submit=True):
    if st.session_state.reply:
        st.markdown(f"↪ 답장 중: {st.session_state.reply}")
    txt = st.text_input("메시지")
    ok = st.form_submit_button("보내기")

if ok and txt:
    msgs.append({
        "type": "answer" if st.session_state.login and st.session_state.reply else "question",
        "text": txt,
        "reply": st.session_state.reply,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    save_msgs(msgs)
    st.session_state.reply=None
    st.rerun()

