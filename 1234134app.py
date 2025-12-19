import streamlit as st
import json, os
from datetime import datetime

# ================= CONFIG =================
st.set_page_config("CHAT", layout="centered")

DATA = "data"
os.makedirs(DATA, exist_ok=True)

USERS = f"{DATA}/users.json"
CHATS = f"{DATA}/chats.json"

def load(p):
    if not os.path.exists(p):
        with open(p, "w", encoding="utf-8") as f:
            json.dump({}, f)
    with open(p, encoding="utf-8") as f:
        return json.load(f)

def save(p, d):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

users = load(USERS)
chats = load(CHATS)

# ================= SESSION =================
if "user" not in st.session_state: st.session_state.user = None
if "chat_with" not in st.session_state: st.session_state.chat_with = None
if "theme" not in st.session_state: st.session_state.theme = "핑크"

# ================= THEME =================
THEMES = {
    "핑크": {
        "bg": "#fff0f6",
        "me": "#ff5fa2",
        "other": "#ffe0ec",
        "text": "#222"
    },
    "다크": {
        "bg": "#0f0f14",
        "me": "#ff5fa2",
        "other": "#2a2a35",
        "text": "#eee"
    },
    "라이트": {
        "bg": "#f6f6f6",
        "me": "#4f8cff",
        "other": "#e8e8e8",
        "text": "#222"
    }
}

t = THEMES[st.session_state.theme]

st.markdown(f"""
<style>
body {{ background:{t['bg']}; color:{t['text']}; }}
.chat-me {{
    background:{t['me']};
    color:white;
    padding:10px 14px;
    border-radius:18px 18px 4px 18px;
    margin:6px 0 6px auto;
    width:fit-content;
    max-width:80%;
}}
.chat-other {{
    background:{t['other']};
    padding:10px 14px;
    border-radius:18px 18px 18px 4px;
    margin:6px 0;
    width:fit-content;
    max-width:80%;
}}
.chat-card {{
    background:white;
    padding:16px;
    border-radius:20px;
    box-shadow:0 8px 30px rgba(0,0,0,.12);
    margin-bottom:12px;
}}
button {{
    border-radius:18px !important;
}}
</style>
""", unsafe_allow_html=True)

# ================= HELPERS =================
def room_id(a, b):
    return "_".join(sorted([a, b]))

def is_online(u):
    return users.get(u, {}).get("online", False)

def unread(me, rid):
    return sum(
        1 for m in chats[rid]["messages"]
        if m["user"] != me and me not in m.get("read", [])
    )

# ================= AUTH =================
st.title("💬 CHAT")

if st.session_state.user is None:
    t1, t2 = st.tabs(["Login", "Sign up"])
    with t1:
        uid = st.text_input("ID")
        if st.button("Login"):
            if uid in users:
                st.session_state.user = uid
                users[uid]["online"] = True
                save(USERS, users)
                st.rerun()
            else:
                st.error("없는 사용자")
    with t2:
        nid = st.text_input("New ID")
        if st.button("Create"):
            if nid in users:
                st.error("이미 있음")
            else:
                users[nid] = {"online": False}
                save(USERS, users)
                st.success("생성 완료")
    st.stop()

me = st.session_state.user

# ================= HEADER =================
c1, c2, c3 = st.columns([2,2,1])
c1.markdown(f"**@{me}** ● 온라인")
c2.selectbox("🎨 테마", THEMES.keys(), key="theme")
if c3.button("로그아웃"):
    users[me]["online"] = False
    save(USERS, users)
    st.session_state.user = None
    st.rerun()

# ================= CHAT LIST =================
st.subheader("📨 채팅")

for u in users:
    if u == me: continue
    rid = room_id(me, u)
    chats.setdefault(rid, {"users": [me, u], "messages": []})
    cnt = unread(me, rid)
    online = "●" if is_online(u) else "○"
    label = f"{online} @{u}"
    if cnt: label += f" 🔴{cnt}"
    if st.button(label):
        st.session_state.chat_with = u

# ================= NEW CHAT =================
with st.expander("➕ 새 채팅"):
    new = st.selectbox("유저 선택", [u for u in users if u != me])
    if st.button("채팅 시작"):
        st.session_state.chat_with = new
        st.rerun()

# ================= CHAT ROOM =================
if st.session_state.chat_with:
    other = st.session_state.chat_with
    rid = room_id(me, other)
    room = chats[rid]

    st.markdown("---")
    status = "온라인 ●" if is_online(other) else "오프라인 ○"
    st.markdown(f"### @{other} ({status})")

    box = st.container()
    with box:
        for m in room["messages"]:
            m.setdefault("read", [])
            if me not in m["read"]:
                m["read"].append(me)
            cls = "chat-me" if m["user"] == me else "chat-other"
            st.markdown(
                f"<div class='{cls}'>{m['text']}<br><small>{m['time']}</small></div>",
                unsafe_allow_html=True
            )

    with st.form("send", clear_on_submit=True):
        msg = st.text_area(
            "",
            placeholder="메시지 입력 (Enter = 줄바꿈)",
            height=90
        )
        send = st.form_submit_button("Send")
        if send and msg.strip():
            room["messages"].append({
                "user": me,
                "text": msg,
                "time": datetime.now().strftime("%H:%M"),
                "read": [me]
            })
            save(CHATS, chats)
            st.rerun()

save(CHATS, chats)
