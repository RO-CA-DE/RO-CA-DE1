# =====================================================
# 말랑 핑크 채팅 웹 – 최종 완성본 v2 (관리자 설정 포함)
# 기준 디자인: 사용자가 처음 보낸 이미지 감성
# 질문 = 오른쪽 / 답변 = 왼쪽
# 모바일 기준, PC에서도 모바일 화면처럼 표시
# =====================================================

import streamlit as st
import json, os
from datetime import datetime

# ---------------- 기본 설정 ----------------
st.set_page_config(page_title="AOUSE Chat", layout="centered")

DATA = "data"
MSG_FILE = f"{DATA}/messages.json"
ADMIN_FILE = f"{DATA}/admin.json"
os.makedirs(DATA, exist_ok=True)

# ---------------- 관리자 기본값 ----------------
def load_admin():
    if not os.path.exists(ADMIN_FILE):
        admin = {
            "id": "admin",
            "password": "1234",
            "name": "아진이",
            "avatar": "https://i.imgur.com/OVC5X8N.png",
            "theme": "rose"
        }
        with open(ADMIN_FILE, "w", encoding="utf-8") as f:
            json.dump(admin, f, ensure_ascii=False, indent=2)
        return admin
    with open(ADMIN_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_admin(admin):
    with open(ADMIN_FILE, "w", encoding="utf-8") as f:
        json.dump(admin, f, ensure_ascii=False, indent=2)

admin = load_admin()

# ---------------- 메시지 ----------------
def load_msgs():
    if not os.path.exists(MSG_FILE):
        return []
    with open(MSG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_msgs(msgs):
    with open(MSG_FILE, "w", encoding="utf-8") as f:
        json.dump(msgs, f, ensure_ascii=False, indent=2)

# ---------------- 세션 ----------------
if "login" not in st.session_state:
    st.session_state.login = False
if "reply_to" not in st.session_state:
    st.session_state.reply_to = None

# ---------------- 테마 ----------------
THEMES = {
    "rose": "#D98B8B",
    "peach": "#F2A7A7",
    "berry": "#C86B85"
}
BUBBLE_COLOR = THEMES.get(admin.get("theme"), "#D98B8B")

# ---------------- 스타일 ----------------
st.markdown(f"""
<style>
body {{ background:#FFF6F6; }}
* {{ font-family:'Pretendard',sans-serif; box-sizing:border-box; }}

.chat {{ max-width:420px; margin:0 auto; padding:24px 14px 130px; }}
@media (min-width:768px){{ .chat{{ max-width:390px; }} }}

.date {{ margin:20px auto; padding:8px 18px; background:#EFEAEA; border-radius:999px;
font-size:13px; color:#555; width:fit-content; }}

.msg {{ display:flex; gap:10px; margin-bottom:18px; }}
.left {{ justify-content:flex-start; }}
.right {{ justify-content:flex-end; }}

.avatar {{ width:42px; height:42px; border-radius:50%; object-fit:cover; }}

.bubble {{ background:{BUBBLE_COLOR}; color:#FFFDFD; padding:14px 18px; border-radius:18px;
max-width:72%; line-height:1.5; letter-spacing:-0.2px;
box-shadow:0 6px 14px rgba(0,0,0,0.18); }}

.name {{ font-size:12px; opacity:0.85; margin-bottom:4px; }}
.text {{ font-size:14.5px; }}
.time {{ font-size:11px; opacity:0.65; margin-top:6px; text-align:right; }}

.reply-quote {{ font-size:12px; opacity:0.6; margin-bottom:8px; border-left:2px solid rgba(255,255,255,0.6); padding-left:8px; }}

section[data-testid="stForm"]{{ position:fixed; bottom:0; left:50%; transform:translateX(-50%);
width:100%; max-width:420px; background:#FFF6F6; padding:10px 14px 14px;
border-top:1px solid rgba(0,0,0,0.05); }}
</style>
""", unsafe_allow_html=True)

# ---------------- 로그인 / 관리자 설정 ----------------
with st.sidebar:
    if not st.session_state.login:
        uid = st.text_input("관리자 ID")
        pw = st.text_input("비밀번호", type="password")
        if st.button("로그인"):
            if uid == admin["id"] and pw == admin["password"]:
                st.session_state.login = True
                st.rerun()
            else:
                st.error("로그인 실패")
    else:
        st.success("관리자 로그인됨")

        admin["name"] = st.text_input("이름", admin["name"])
        admin["avatar"] = st.text_input("프사 URL", admin["avatar"])
        admin["theme"] = st.selectbox("테마", list(THEMES.keys()), index=list(THEMES.keys()).index(admin["theme"]))

        if st.button("설정 저장"):
            save_admin(admin)
            st.rerun()

        if st.button("로그아웃"):
            st.session_state.login = False
            st.session_state.reply_to = None
            st.rerun()

# ---------------- 채팅 출력 ----------------
msgs = load_msgs()
current_date = None

st.markdown('<div class="chat">', unsafe_allow_html=True)

for i, m in enumerate(msgs):
    d = m["time"][:10]
    if d != current_date:
        st.markdown(f'<div class="date">{d}</div>', unsafe_allow_html=True)
        current_date = d

    side = "left" if m["type"] == "answer" else "right"
    st.markdown(f'<div class="msg {side}">', unsafe_allow_html=True)

    if side == "left":
        st.markdown(f'<img class="avatar" src="{admin["avatar"]}">', unsafe_allow_html=True)

    st.markdown('<div class="bubble">', unsafe_allow_html=True)

    if m.get("reply"):
        st.markdown(f'<div class="reply-quote">{m["reply"]}</div>', unsafe_allow_html=True)

    if side == "left":
        st.markdown(f'<div class="name">{admin["name"]}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="text">{m["text"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="time">{m["time"][-5:]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if m["type"] == "question" and st.session_state.login:
        if st.button("답장", key=f"r{i}"):
            st.session_state.reply_to = m["text"]
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- 입력 ----------------
with st.form("send", clear_on_submit=True):
    if st.session_state.reply_to:
        st.markdown(f"↪ 답장 중: {st.session_state.reply_to}")
        if st.form_submit_button("답장 취소"):
            st.session_state.reply_to = None
            st.rerun()

    txt = st.text_input("메시지 입력")
    send = st.form_submit_button("보내기")

if send and txt:
    msgs.append({
        "type": "answer" if st.session_state.login and st.session_state.reply_to else "question",
        "text": txt,
        "reply": st.session_state.reply_to,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    save_msgs(msgs)
    st.session_state.reply_to = None
    st.rerun()
