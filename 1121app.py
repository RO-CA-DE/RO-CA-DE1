import streamlit as st
import json, os
from datetime import datetime

# ================= BASIC =================
st.set_page_config(page_title="AOUSE", layout="centered")

DATA="data"
POSTS=f"{DATA}/posts.json"
USERS=f"{DATA}/users.json"
os.makedirs(DATA, exist_ok=True)

def load(p):
    if not os.path.exists(p):
        with open(p,"w",encoding="utf-8") as f: json.dump({},f)
    with open(p,"r",encoding="utf-8") as f: return json.load(f)

def save(p,d):
    with open(p,"w",encoding="utf-8") as f:
        json.dump(d,f,ensure_ascii=False,indent=2)

posts=load(POSTS)
users=load(USERS)

# ================= SESSION =================
for k,v in {
    "user":None,
    "open_post":None,
    "edit_post":None
}.items():
    if k not in st.session_state:
        st.session_state[k]=v

# ================= STYLE =================
st.markdown("""
<style>
body {background:#fff0f6;}
.card {
 background:white; padding:18px; border-radius:18px;
 margin-bottom:14px; box-shadow:0 6px 18px rgba(255,105,180,.15)
}
.title {
 font-size:20px; font-weight:700; cursor:pointer;
}
.content {margin-top:12px; font-size:15px; line-height:1.6}
.meta {font-size:12px; opacity:.6}
.pin {color:#ff5fa2}
button {border-radius:18px!important}
</style>
""", unsafe_allow_html=True)

# ================= AUTH =================
st.title("💗 AOUSE")

if st.session_state.user is None:
    uid=st.text_input("아이디")
    if st.button("로그인"):
        users.setdefault(uid,{})
        save(USERS,users)
        st.session_state.user=uid
        st.rerun()
    st.stop()

me=st.session_state.user
st.caption(f"@{me}")

# ================= WRITE =================
with st.expander("✍️ 새 포스트"):
    t=st.text_input("제목")
    c=st.text_area("내용")
    if st.button("게시"):
        pid=str(datetime.now().timestamp())
        posts[pid]={
            "title":t,
            "content":c,
            "user":me,
            "time":datetime.now().strftime("%Y-%m-%d %H:%M"),
            "pin":False
        }
        save(POSTS,posts)
        st.rerun()

# ================= FEED =================
st.subheader("📰 Feed")

# 핀 우선 정렬
sorted_posts = sorted(
    posts.items(),
    key=lambda x: (not x[1].get("pin",False), x[1]["time"]),
    reverse=True
)

for pid,p in sorted_posts:
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        # 제목 클릭 토글
        if st.button(
            f"{'📌 ' if p.get('pin') else ''}{p['title']}",
            key=f"title{pid}"
        ):
            st.session_state.open_post = None if st.session_state.open_post==pid else pid

        st.markdown(
            f"<div class='meta'>@{p['user']} · {p['time']}</div>",
            unsafe_allow_html=True
        )

        # 내용 (토글)
        if st.session_state.open_post==pid:
            st.markdown(
                f"<div class='content'>{p['content']}</div>",
                unsafe_allow_html=True
            )

        # 내 글 관리
        if p["user"]==me:
            c1,c2,c3=st.columns(3)

            # 핀
            if c1.button("📌 핀", key=f"pin{pid}"):
                p["pin"]=not p.get("pin",False)
                save(POSTS,posts); st.rerun()

            # 수정
            if c2.button("✏️ 수정", key=f"edit{pid}"):
                st.session_state.edit_post=pid

            # 삭제
            if c3.button("🗑 삭제", key=f"del{pid}"):
                posts.pop(pid)
                save(POSTS,posts); st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# ================= EDIT =================
if st.session_state.edit_post:
    ep=st.session_state.edit_post
    st.markdown("---")
    st.subheader("✏️ 포스트 수정")

    nt=st.text_input("제목", posts[ep]["title"])
    nc=st.text_area("내용", posts[ep]["content"])

    if st.button("저장"):
        posts[ep]["title"]=nt
        posts[ep]["content"]=nc
        save(POSTS,posts)
        st.session_state.edit_post=None
        st.rerun()

    if st.button("취소"):
        st.session_state.edit_post=None
        st.rerun()

