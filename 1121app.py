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
defaults={
 "user":None,
 "tab":"home",
 "open_comments":{},
 "edit_post":None
}
for k,v in defaults.items():
    if k not in st.session_state: st.session_state[k]=v

# ================= STYLE =================
st.markdown("""
<style>
body {background:#ffe6f0;}
.main > div {max-width:420px; padding-bottom:90px;}
.header {
 text-align:center; font-size:26px; font-weight:800;
 color:#ff5fa2; margin:18px 0;
}
.card {
 background:white; border-radius:22px;
 padding:16px; margin-bottom:14px;
 box-shadow:0 8px 24px rgba(255,95,162,.18);
}
.title {font-size:18px; font-weight:700;}
.meta {font-size:12px; opacity:.6; margin-top:4px;}
.content {margin-top:12px; line-height:1.65;}
.actions button {width:100%; border-radius:14px!important;}
.like {color:#ff5fa2; font-weight:700;}
.comment {background:#fff5fa; padding:8px 12px; border-radius:14px; margin-top:6px;}
/* 탭바 */
.tabbar {
 position:fixed; bottom:0; left:0; right:0;
 background:white; border-top:1px solid #ffd1e3;
 display:flex; justify-content:space-around;
 padding:10px 0;
}
.tabbar button {
 background:none!important; border:none!important;
 font-size:14px!important;
}
</style>
""", unsafe_allow_html=True)

# ================= AUTH =================
st.markdown("<div class='header'>AOUSE</div>", unsafe_allow_html=True)

if st.session_state.user is None:
    uid=st.text_input("아이디")
    if st.button("로그인"):
        users.setdefault(uid,{})
        save(USERS,users)
        st.session_state.user=uid
        st.rerun()
    st.stop()

me=st.session_state.user

# ================= HELPERS =================
def post_card(pid,p):
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"<div class='title'>{'📌 ' if p['pin'] else ''}{p['title']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='meta'>@{p['user']} · {p['time']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='content'>{p['content']}</div>", unsafe_allow_html=True)

    # 좋아요
    liked = me in p["likes"]
    if st.button(f"❤️ {len(p['likes'])}", key=f"like{pid}"):
        if liked: p["likes"].remove(me)
        else: p["likes"].append(me)
        save(POSTS,posts); st.rerun()

    # 댓글
    if st.button(
        f"💬 댓글 {len(p['comments'])}",
        key=f"cmt{pid}"
    ):
        st.session_state.open_comments[pid]=not st.session_state.open_comments.get(pid,False)

    if st.session_state.open_comments.get(pid):
        for c in p["comments"]:
            st.markdown(
                f"<div class='comment'><b>@{c['user']}</b> {c['text']}</div>",
                unsafe_allow_html=True
            )
        txt=st.text_input("댓글", key=f"ct{pid}")
        if st.button("등록", key=f"cb{pid}") and txt.strip():
            p["comments"].append({
                "user":me,
                "text":txt,
                "time":datetime.now().strftime("%H:%M")
            })
            save(POSTS,posts); st.rerun()

    # 관리
    if p["user"]==me:
        c1,c2,c3=st.columns(3)
        if c1.button("📌 핀", key=f"pin{pid}"):
            p["pin"]=not p["pin"]; save(POSTS,posts); st.rerun()
        if c2.button("✏️ 수정", key=f"edit{pid}"):
            st.session_state.edit_post=pid
        if c3.button("🗑 삭제", key=f"del{pid}"):
            posts.pop(pid); save(POSTS,posts); st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ================= TABS =================
if st.session_state.tab=="home":
    st.subheader("📌 Pinned")
    for pid,p in posts.items():
        if p["pin"]: post_card(pid,p)

    st.subheader("📰 Feed")
    for pid,p in sorted(posts.items(), key=lambda x:x[1]["time"], reverse=True):
        post_card(pid,p)

elif st.session_state.tab=="write":
    st.subheader("✍️ 새 포스트")
    t=st.text_input("제목")
    c=st.text_area("내용", height=140)
    if st.button("게시"):
        pid=str(datetime.now().timestamp())
        posts[pid]={
            "title":t,"content":c,"user":me,
            "time":datetime.now().strftime("%Y-%m-%d %H:%M"),
            "pin":False,"likes":[],"comments":[]
        }
        save(POSTS,posts); st.rerun()

elif st.session_state.tab=="profile":
    st.subheader(f"👤 @{me}")
    my=[p for p in posts.items() if p[1]["user"]==me]
    st.caption(f"게시물 {len(my)} · 좋아요 {sum(len(p[1]['likes']) for p in my)}")
    for pid,p in my:
        post_card(pid,p)

# ================= EDIT =================
if st.session_state.edit_post:
    ep=st.session_state.edit_post
    st.markdown("---")
    st.subheader("✏️ 수정")
    nt=st.text_input("제목", posts[ep]["title"])
    nc=st.text_area("내용", posts[ep]["content"])
    if st.button("저장"):
        posts[ep]["title"]=nt
        posts[ep]["content"]=nc
        save(POSTS,posts)
        st.session_state.edit_post=None
        st.rerun()

# ================= TABBAR =================
st.markdown("""
<div class='tabbar'>
<form method="post">
</form>
</div>
""", unsafe_allow_html=True)

c1,c2,c3 = st.columns(3)
if c1.button("🏠 홈"): st.session_state.tab="home"; st.rerun()
if c2.button("✍️ 작성"): st.session_state.tab="write"; st.rerun()
if c3.button("👤 프로필"): st.session_state.tab="profile"; st.rerun()
