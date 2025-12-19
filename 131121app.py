import streamlit as st
import json, os, uuid
from datetime import datetime

# ================= CONFIG =================
st.set_page_config("AOUSE", layout="centered")

DATA="data"
UPLOADS="uploads"
os.makedirs(DATA, exist_ok=True)
os.makedirs(UPLOADS, exist_ok=True)

FILES = {
    "users": f"{DATA}/users.json",
    "posts": f"{DATA}/posts.json",
    "comments": f"{DATA}/comments.json",
    "likes": f"{DATA}/likes.json",
    "reactions": f"{DATA}/reactions.json",
    "follows": f"{DATA}/follows.json"
}

def load(p):
    if not os.path.exists(p):
        with open(p,"w",encoding="utf-8") as f:
            json.dump({},f)
    with open(p,encoding="utf-8") as f:
        return json.load(f)

def save(p,d):
    with open(p,"w",encoding="utf-8") as f:
        json.dump(d,f,ensure_ascii=False,indent=2)

users=load(FILES["users"])
posts=load(FILES["posts"])
comments=load(FILES["comments"])
likes=load(FILES["likes"])
reactions=load(FILES["reactions"])
follows=load(FILES["follows"])

# ================= STYLE =================
st.markdown("""
<style>
body {background:#fff0f6;}
h1,h2,h3 {color:#ff4d8d;}
.card {
 background:white;
 padding:20px;
 border-radius:20px;
 box-shadow:0 10px 25px rgba(255,105,180,.15);
 margin-bottom:20px;
}
button {
 background:linear-gradient(135deg,#ff7eb3,#ff4d8d)!important;
 color:white!important;
 border-radius:20px!important;
 border:none!important;
}
img {border-radius:18px;}
hr {border:none;height:1px;background:#ffd6e8;}
.badge {
 display:inline-block;
 padding:4px 10px;
 border-radius:12px;
 background:#ffe0ec;
 color:#ff4d8d;
 font-size:12px;
 margin-right:5px;
}
</style>
""",unsafe_allow_html=True)

# ================= SESSION =================
if "user" not in st.session_state:
    st.session_state.user=None
if "page" not in st.session_state:
    st.session_state.page="feed"
if "view" not in st.session_state:
    st.session_state.view=None

# ================= AUTH =================
st.title("💗 AOUSE")

if st.session_state.user is None:
    t1,t2=st.tabs(["Login","Sign up"])
    with t1:
        uid=st.text_input("ID")
        if st.button("Login"):
            if uid in users:
                st.session_state.user=uid
                st.rerun()
            else: st.error("No user")
    with t2:
        nid=st.text_input("New ID")
        if st.button("Create"):
            if nid in users:
                st.error("Already exists")
            else:
                users[nid]={"bio":""}
                follows[nid]=[]
                save(FILES["users"],users)
                save(FILES["follows"],follows)
                st.success("Created!")
    st.stop()

me=st.session_state.user

# ================= NAV =================
c1,c2,c3=st.columns(3)
if c1.button("🏠 Feed"): st.session_state.page="feed"
if c2.button("👤 Profile"): st.session_state.page="profile"
if c3.button("🚪 Logout"):
    st.session_state.user=None
    st.rerun()

# ================= NEW POST =================
st.markdown("<div class='card'>",unsafe_allow_html=True)
st.subheader("➕ New Post")
with st.form("post"):
    txt=st.text_area("Write something")
    emo=st.selectbox("Emotion",["💗","💔","🔥","😶","🌸"])
    img=st.file_uploader("Image",["png","jpg","jpeg"])
    if st.form_submit_button("Post"):
        pid=str(uuid.uuid4())
        path=""
        if img:
            path=f"{UPLOADS}/{pid}_{img.name}"
            with open(path,"wb") as f: f.write(img.getbuffer())
        posts[pid]={
            "user":me,"text":txt,"emotion":emo,
            "image":path,"time":datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        save(FILES["posts"],posts)
        st.rerun()
st.markdown("</div>",unsafe_allow_html=True)

# ================= PROFILE =================
if st.session_state.page=="profile":
    st.markdown("<div class='card'>",unsafe_allow_html=True)
    st.subheader(f"@{me}")
    bio=st.text_input("Bio",users[me].get("bio",""))
    if st.button("Save bio"):
        users[me]["bio"]=bio
        save(FILES["users"],users)
    st.markdown(f"Following {len(follows.get(me,[]))}")
    st.markdown("</div>",unsafe_allow_html=True)

# ================= FEED =================
st.subheader("🖼 Feed")
for pid,p in sorted(posts.items(),key=lambda x:x[1]["time"],reverse=True):
    if st.session_state.page=="profile" and p["user"]!=me:
        continue

    st.markdown("<div class='card'>",unsafe_allow_html=True)
    st.markdown(f"**@{p['user']}** <span class='badge'>{p['emotion']}</span>",unsafe_allow_html=True)
    st.caption(p["time"])

    if p["image"]: st.image(p["image"],use_column_width=True)
    st.markdown(p["text"])

    likes.setdefault(pid,[])
    reactions.setdefault(pid,{"😭":0,"😍":0,"🔥":0})

    c1,c2,c3,c4=st.columns(4)
    if c1.button(f"❤️ {len(likes[pid])}",key=f"l{pid}"):
        if me not in likes[pid]:
            likes[pid].append(me)
            save(FILES["likes"],likes)
            st.rerun()
    if c2.button("😭",key=f"r1{pid}"):
        reactions[pid]["😭"]+=1; save(FILES["reactions"],reactions); st.rerun()
    if c3.button("😍",key=f"r2{pid}"):
        reactions[pid]["😍"]+=1; save(FILES["reactions"],reactions); st.rerun()
    if c4.button("🔥",key=f"r3{pid}"):
        reactions[pid]["🔥"]+=1; save(FILES["reactions"],reactions); st.rerun()

    st.markdown(f"😭 {reactions[pid]['😭']} · 😍 {reactions[pid]['😍']} · 🔥 {reactions[pid]['🔥']}")

    comments.setdefault(pid,[])
    for c in comments[pid]:
        st.markdown(f"💬 **@{c['user']}** {c['text']}")

    with st.form(f"c{pid}"):
        ct=st.text_input("Comment",key=f"ct{pid}")
        if st.form_submit_button("Send"):
            comments[pid].append({"user":me,"text":ct})
            save(FILES["comments"],comments)
            st.rerun()

    st.markdown("</div>",unsafe_allow_html=True)
