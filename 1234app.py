import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Bubble Chat",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ------------------------------
# CSS (디자인 핵심)
# ------------------------------
st.markdown("""
<style>
body {
    background-color: #FFF5F5;
}
.chat {
    max-width: 420px;
    margin: auto;
}
.date {
    text-align: center;
    margin: 16px 0;
    font-size: 13px;
    color: #777;
}
.date span {
    background: white;
    padding: 4px 14px;
    border-radius: 999px;
    box-shadow: 0 4px 12px rgba(0,0,0,.08);
}
.msg {
    display: flex;
    gap: 8px;
    margin-bottom: 14px;
}
.avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
}
.name {
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 4px;
}
.bubble {
    padding: 10px 14px;
    border-radius: 18px;
    max-width: 260px;
    word-break: break-word;
    white-space: pre-wrap;
    box-shadow: 0 6px 18px rgba(0,0,0,.12);
}
.admin {
    background: #D98989;
    color: white;
}
.fan {
    background: #E5E5EA;
    color: #333;
}
.input-box {
    position: sticky;
    bottom: 0;
    background: white;
    padding: 12px;
    border-top: 1px solid #eee;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------
# 세션 상태
# ------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "user": "admin",
            "name": "아진",
            "verified": True,
            "avatar": "https://i.pravatar.cc/100?img=5",
            "text": "안농 🙌🏻",
            "date": "2025.12.18"
        },
        {
            "user": "admin",
            "name": "아진",
            "verified": True,
            "avatar": "https://i.pravatar.cc/100?img=5",
            "text": "올 한해도 벌써 끝이라는 사실이…",
            "date": "2025.12.18"
        }
    ]

# ------------------------------
# 렌더 함수
# ------------------------------
def render_message(m):
    badge = "✔" if m.get("verified") else ""
    role = "admin" if m["user"] == "admin" else "fan"

    st.markdown(f"""
    <div class="msg">
        <img class="avatar" src="{m['avatar']}">
        <div>
            <div class="name">{m['name']} {badge}</div>
            <div class="bubble {role}">{m['text']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ------------------------------
# UI
# ------------------------------
st.markdown('<div class="chat">', unsafe_allow_html=True)

last_date = ""
for m in st.session_state.messages:
    if m["date"] != last_date:
        st.markdown(
            f'<div class="date"><span>{m["date"]}</span></div>',
            unsafe_allow_html=True
        )
        last_date = m["date"]
    render_message(m)

st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------
# 입력창
# ------------------------------
st.markdown('<div class="input-box">', unsafe_allow_html=True)
col1, col2 = st.columns([5,1])

with col1:
    text = st.text_input(
        "메시지",
        placeholder="메시지를 입력하세요",
        label_visibility="collapsed"
    )

with col2:
    send = st.button("전송")

if send and text.strip():
    st.session_state.messages.append({
        "user": "fan",
        "name": "팬",
        "verified": False,
        "avatar": "https://i.pravatar.cc/100?img=8",
        "text": text,
        "date": datetime.now().strftime("%Y.%m.%d")
    })
    st.experimental_rerun()

st.markdown('</div>', unsafe_allow_html=True)
