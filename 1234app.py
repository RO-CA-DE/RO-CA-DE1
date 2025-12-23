import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Azin Pink Chat", layout="centered")

# =====================
# SESSION STATE
# =====================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "role" not in st.session_state:
    st.session_state.role = "fan"

if "admin_profile" not in st.session_state:
    st.session_state.admin_profile = {
        "name": "아진",
        "avatar": "https://i.pravatar.cc/100?img=5",
        "color": "#FF6F91"  # 핑크 기본값
    }

# =====================
# SIDEBAR (LOGIN & ADMIN SETTINGS)
# =====================
with st.sidebar:
    st.title("🎀 설정")

    st.subheader("로그인")
    st.session_state.role = st.radio(
        "역할 선택",
        ["fan", "admin"],
        format_func=lambda x: "팬" if x == "fan" else "관리자(아진)"
    )

    if st.session_state.role == "admin":
        st.subheader("👩‍💼 관리자 설정")

        st.session_state.admin_profile["name"] = st.text_input(
            "이름",
            st.session_state.admin_profile["name"]
        )

        st.session_state.admin_profile["avatar"] = st.text_input(
            "프로필 이미지 URL",
            st.session_state.admin_profile["avatar"]
        )

        st.session_state.admin_profile["color"] = st.color_picker(
            "말풍선 색상",
            st.session_state.admin_profile["color"]
        )

    st.divider()

    if st.button("🧹 메시지 전체 초기화"):
        st.session_state.messages = []
        st.experimental_rerun()

# =====================
# CSS (PINK THEME)
# =====================
st.markdown(f"""
<style>
body {{
    background:#FFF0F5;
}}
.chat {{
    max-width:420px;
    margin:auto;
}}
.date {{
    text-align:center;
    margin:20px 0;
    font-size:13px;
    color:#B85C8A;
}}
.date span {{
    background:white;
    padding:4px 14px;
    border-radius:999px;
    box-shadow:0 4px 12px rgba(255,111,145,.25);
}}
.msg {{
    display:flex;
    margin-bottom:14px;
    gap:8px;
}}
.right {{
    flex-direction:row-reverse;
}}
.avatar {{
    width:36px;
    height:36px;
    border-radius:50%;
}}
.name {{
    font-size:12px;
    font-weight:600;
    margin-bottom:4px;
    color:#8A3C66;
}}
.bubble {{
    padding:10px 14px;
    border-radius:18px;
    max-width:260px;
    word-break:break-word;
    white-space:pre-wrap;
    box-shadow:0 6px 18px rgba(255,111,145,.35);
}}
.admin {{
    background:{st.session_state.admin_profile["color"]};
    color:white;
}}
.fan {{
    background:#FFE4EC;
    color:#5A2A42;
}}
.input {{
    position:sticky;
    bottom:0;
    background:white;
    padding:12px;
    border-top:1px solid #FFD1E1;
}}
</style>
""", unsafe_allow_html=True)

# =====================
# RENDER FUNCTION (SAFE)
# =====================
def render(m):
    side = "right" if m.get("side") == "right" else ""
    role = "admin" if m.get("role") == "admin" else "fan"

    st.markdown(f"""
    <div class="msg {side}">
        <img class="avatar" src="{m.get('avatar', '')}">
        <div>
            <div class="name">{m.get('name', '')}</div>
            <div class="bubble {role}">{m.get('text', '')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =====================
# CHAT UI
# =====================
st.markdown('<div class="chat">', unsafe_allow_html=True)

last_date = ""
for m in st.session_state.messages:
    date = m.get("date", "")
    if date != last_date:
        st.markdown(
            f'<div class="date"><span>{date}</span></div>',
            unsafe_allow_html=True
        )
        last_date = date
    render(m)

st.markdown('</div>', unsafe_allow_html=True)

# =====================
# INPUT
# =====================
st.markdown('<div class="input">', unsafe_allow_html=True)
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
    is_admin = st.session_state.role == "admin"

    st.session_state.messages.append({
        "role": "admin" if is_admin else "fan",
        "name": st.session_state.admin_profile["name"] if is_admin else "팬",
        "avatar": st.session_state.admin_profile["avatar"] if is_admin else "https://i.pravatar.cc/100?img=8",
        "text": text,
        "side": "right",
        "date": datetime.now().strftime("%Y.%m.%d")
    })
    st.experimental_rerun()

st.markdown('</div>', unsafe_allow_html=True)



