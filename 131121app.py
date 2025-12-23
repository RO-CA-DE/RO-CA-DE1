import streamlit as st
import json, os, uuid, time

# ================= BASIC =================
st.set_page_config(page_title="AOUSE", layout="centered")

DATA="data"
os.makedirs(DATA, exist_ok=True)

USERS=f"{DATA}/users.json"
POSTS=f"{DATA}/posts.json"

def load(p, d):
    if os.path.exists(p):
        try:
            return json.load(open(p, encoding="utf-8"))
        except:
            return d
    return d

def save(p, d):
    json.dump(d, open(p,"w",encoding="utf-8"), ensure_ascii=False, indent=2)

users=load(USERS,{})
posts=load(POSTS,{})

# ================= SESSION =================
if "uid" not in st.session_state:
    st.session_state.uid=None
if "tab" not in st.session_state:
    st.session_state.tab="home"
if "open_post" not in st.session_state:
    st.session_state.open_post=None

# ================= THEME =================
st.markdown("""
<style>
body { background:#ffe6f0; }
.card {
 background:white;
 border-radius:16px;
 padding:14px;
 margin:10px 0;
}
.title { font-weight:700; font-size:18px; }
.content { white-space:pre-wrap; margin-top:8px; }
.tab {
 position:fixed;
 bottom:0; left:0; right:0;
 background:white;
 display:flex;
 justify-content:space-around;
 padding:12px;
 border-top:1px solid #eee;
}
</style>
""", unsafe_allow_html=True)

# ================= LOGIN =================
st.markdown("## 🌸 AOUSE")

if not st.session_state.uid:
    name=st.text_input("이름")
    if st.button("시작하기") and name:
        uid=str(uuid.uuid4())
        users[uid]={"name":name}
        save(USERS, users)
        st.session_state.uid=uid
        st.rerun()
    st.stop()

me=users[st.session_state.uid]

# ================= HOME =================
if st.session_state.tab=="home":
    st.markdown("### 🏠 홈")

    pinned=[p for p in posts.values() if p.get("pin")]
    normal=[p for p in posts.values() if not p.get("pin")]

    for p in pinned + normal:
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)

            if st.button("📌 "+p["title"], key=p["id"]):
                st.session_state.open_post = None if st.session_state.open_post==p["id"] else p["id"]

            if st.session_state.open_post==p["id"]:
                st.markdown(f"<div class='content'>{p['content']}</div>", unsafe_allow_html=True)

                col1,col2,col3=st.columns(3)
                with col1:
                    if st.button(f"❤️ {p['likes']}", key="l"+p["id"]):
                        p["likes"]+=1
                        save(POSTS, posts)
                        st.rerun()
                with col2:
                    if st.button("✏️", key="e"+p["id"]) and p["uid"]==st.session_state.uid:
                        p["content"]=st.text_area("수정", p["content"])
                        if st.button("저장", key="s"+p["id"]):
                            save(POSTS, posts)
                            st.rerun()
                with col3:
                    if st.button("🗑", key="d"+p["id"]) and p["uid"]==st.session_state.uid:
                        posts.pop(p["id"])
                        save(POSTS, posts)
                        st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

# ================= WRITE =================
if st.session_state.tab=="write":
    st.markdown("### ✍️ 작성")

    title=st.text_input("제목")
    content=st.text_area("내용 (줄바꿈 가능)", height=200)

    if st.button("게시"):
        pid=str(uuid.uuid4())
        posts[pid]={
            "id":pid,
            "uid":st.session_state.uid,
            "title":title,
            "content":content,
            "likes":0,
            "pin":False,
            "time":time.time()
        }
        save(POSTS, posts)
        st.session_state.tab="home"
        st.rerun()

# ================= PROFILE =================
if st.session_state.tab=="profile":
    st.markdown("### 👤 프로필")
    st.markdown(f"**{me['name']}**")

    for p in posts.values():
        if p["uid"]==st.session_state.uid:
            st.markdown(f"- {p['title']}")

# ================= TAB BAR =================
st.markdown(f"""
<div class="tab">
 <button onclick="window.location.reload()">홈</button>
 <button onclick="window.location.reload()">작성</button>
 <button onclick="window.location.reload()">프로필</button>
</div>
""", unsafe_allow_html=True)

