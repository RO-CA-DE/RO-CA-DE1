import streamlit as st
import json, os
from datetime import datetime

# ================= CONFIG =================
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
if "user" not in st.session_state: st.session_state.user=None
if "open_posts" not in st.session_state: st.session_state.open_posts={}
if "edit_post" not in st.session_state: st.session_state.edit_post=None

# ================= MOBILE STYLE =================
st.markdown("""
<style>
/* 전체 화면 모바일 폭 */
.main > div {
  max-width: 420px;
  padding: 0 12px;
}

/* 헤더 */
.header {
  text-align:center;
  font-size:26px;
  font-weight:800;
  margin:18px 0 8px;
  color:#ff5fa2;
}

/* 카드 */
.card {
  background:white;
  border-radius:22px;
  padding:16px 16px 14px;
  margin-bottom:14px;
  box-shadow:0 8px 24px rgba(255,95,162,.18);
}

/* 제목 */
.title-btn button {
  width:100%;
  text-align:left;
  font-size:18px!important;
  font-weight:700!important;
  background:none!important;
  border:none!important;
  padding:0!important;
  color:#222!important;
}

/* 메타 */
.meta {
  font-size:12px;
  opacity:.6;
  margin-top:4px;
}

/* 내용 */
.content {
  margin-top:14px;
  font-size:15px;
  line-height:1.65;
}

/* 관리 버튼 */
.manage button {
  width:100%;
  border-radius:14px!important;
  font-size:13px!important;
}

/* 작성 영역 */
.write textarea {
  border-radius:18px;
}

/* 핀 */
.pin {
  color:#ff5fa2;
}
</style>
""", unsafe_allow_html=True)

# ================= AUTH =================
st.markdown("<div class='header'>AOUSE</div>", unsafe_allow_html=True)

if st.session_state.user is None:
    uid=st.text_input("아이디", placeholder="아이디 입력")
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
    with st.container():
        st.markdown("<div class='write'>", unsafe_allow_html=True)
        t=st.text_input("제목")
        c=st.text_area("내용", height=120)
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
        st.markdown("</div>", unsafe_allow_html=True)

# ================= FEED =================
st.subheader("📰 Feed")

sorted_posts = sorted(
    posts.items(),
    key=lambda x: (not x[1].get("pin",False), x[1]["time"]),
    reverse=True
)

for pid,p in sorted_posts:
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        # 제목 토글
        is_open = st.session_state.open_posts.get(pid, False)
        col1,col2 = st.columns([8,1])

        with col1:
            if st.button(
                f"{'📌 ' if p.get('pin') else ''}{p['title']}",
                key=f"title{pid}",
                help="눌러서 열기/닫기"
            ):
                st.session_state.open_posts[pid] = not is_open

        with col2:
            st.markdown("▾" if is_open else "▸")

        st.markdown(
            f"<div class='meta'>@{p['user']} · {p['time']}</div>",
            unsafe_allow_html=True
        )

        if is_open:
            st.markdown(
                f"<div class='content'>{p['content']}</div>",
                unsafe_allow_html=True
            )

        # 관리 버튼
        if p["user"]==me:
            m1,m2,m3 = st.columns(3)
            with m1:
                if st.button("📌 핀", key=f"pin{pid}"):
                    p["pin"]=not p.get("pin",False)
                    save(POSTS,posts); st.rerun()
            with m2:
                if st.button("✏️ 수정", key=f"edit{pid}"):
                    st.session_state.edit_post=pid
            with m3:
                if st.button("🗑 삭제", key=f"del{pid}"):
                    posts.pop(pid)
                    save(POSTS,posts); st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# ================= EDIT =================
if st.session_state.edit_post:
    ep=st.session_state.edit_post
    st.markdown("---")
    st.subheader("✏️ 포스트 수정")

    nt=st.text_input("제목", posts[ep]["title"])
    nc=st.text_area("내용", posts[ep]["content"], height=140)

    c1,c2=st.columns(2)
    if c1.button("저장"):
        posts[ep]["title"]=nt
        posts[ep]["content"]=nc
        save(POSTS,posts)
        st.session_state.edit_post=None
        st.rerun()
    if c2.button("취소"):
        st.session_state.edit_post=None
        st.rerun()
