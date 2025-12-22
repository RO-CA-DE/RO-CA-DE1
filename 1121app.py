import streamlit as st
import json, os, uuid, time
from PIL import Image

# ================= BASIC =================
st.set_page_config(page_title="AOUSE CHAT", layout="centered")

DATA="data"
UPLOAD_IMG="uploads/images"
UPLOAD_PF="uploads/profiles"
USERS=f"{DATA}/users.json"
CHATS=f"{DATA}/chats.json"
THEMES=f"{DATA}/themes.json"

os.makedirs(DATA, exist_ok=True)
os.makedirs(UPLOAD_IMG, exist_ok=True)
os.makedirs(UPLOAD_PF, exist_ok=True)

def init(path, default):
    if not os.path.exists(path):
        with open(path,"w") as f: json.dump(default,f,indent=2)

init(USERS,{})
init(CHATS,{})
init(THEMES,{
    "Pink":{"bg":"#ffe6f0","card":"#ffffff","me":"#ff5fa2","text":"#222"},
    "Dark":{"bg":"#0f0f14","card":"#1c1c24","me":"#3b82f6","text":"#f5f5f5"}
})

def load(p): return json.load(open(p))
def save(p,d): json.dump(d,open(p,"w"),indent=2)

users=load(USERS)
chats=load(CHATS)
themes=load(THEMES)

# ================= SESSION =================
for k in ["uid","chat","page"]:
    if k not in st.session_state:
        st.session_state[k]=None

# ================= LOGIN =================
if not st.session_state.uid:
    st.markdown("## 💬 AOUSE CHAT")
    name=st.text_input("이름")
    if st.button("시작"):
        uid=str(uuid.uuid4())
        users[uid]={
            "name":name,
            "pf":"",
            "theme":"Pink"
        }
        save(USERS,users)
        st.session_state.uid=uid
        st.rerun()
    st.stop()

me=users[st.session_state.uid]
theme=themes[me["theme"]]

# ================= STYLE =================
st.markdown(f"""
<style>
body {{ background:{theme['bg']}; }}
.app {{ max-width:420px;margin:auto; }}
.card {{
 background:{theme['card']};
 border-radius:20px;
 padding:14px;
 margin:8px 0;
}}
.msg {{
 padding:12px;
 border-radius:18px;
 max-width:80%;
 margin:6px 0;
}}
.me {{ background:{theme['me']}; color:white; margin-left:auto; }}
.other {{ background:#eee; }}
.small {{ font-size:11px; opacity:.6; }}
</style>
""",unsafe_allow_html=True)

# ================= SETTINGS PAGE =================
if st.session_state.page=="settings":
    st.markdown("## ⚙️ 프로필 설정")

    if me["pf"]:
        st.image(me["pf"], width=100)

    pf=st.file_uploader("프로필 사진", type=["png","jpg","jpeg"])
    name=st.text_input("이름", me["name"])

    if pf:
        path=f"{UPLOAD_PF}/{uuid.uuid4()}.png"
        open(path,"wb").write(pf.read())
        me["pf"]=path

    me["name"]=name
    users[st.session_state.uid]=me
    save(USERS,users)

    st.markdown("### 🎨 테마 선택")
    me["theme"]=st.selectbox("테마", themes.keys(), index=list(themes).index(me["theme"]))
    save(USERS,users)

    st.markdown("### ➕ 테마 추가")
    tname=st.text_input("테마 이름")
    bg=st.color_picker("배경")
    card=st.color_picker("카드")
    meb=st.color_picker("내 말풍선")
    txt=st.color_picker("텍스트")

    if st.button("테마 추가"):
        themes[tname]={"bg":bg,"card":card,"me":meb,"text":txt}
        save(THEMES,themes)
        me["theme"]=tname
        save(USERS,users)
        st.success("추가 완료")

    if st.button("← 돌아가기"):
        st.session_state.page=None
        st.rerun()

    st.stop()

# ================= HEADER =================
c1,c2=st.columns([8,1])
with c1:
    st.markdown("## 💬 채팅")
with c2:
    if st.button("⚙️"):
        st.session_state.page="settings"
        st.rerun()

# ================= CHAT LIST =================
if not st.session_state.chat:
    if st.button("➕ 1:1 채팅"):
        cid=str(uuid.uuid4())
        chats[cid]={"name":"1:1 채팅","members":[st.session_state.uid],"msgs":[],"pin":False}
        save(CHATS,chats)

    for cid,c in chats.items():
        if st.session_state.uid in c["members"]:
            if st.button(("📌 " if c["pin"] else "")+c["name"], key=cid):
                st.session_state.chat=cid
                st.rerun()
    st.stop()

# ================= CHAT ROOM =================
chat=chats[st.session_state.chat]
others=[u for u in chat["members"] if u!=st.session_state.uid]

if others:
    o=users[others[0]]
    cols=st.columns([1,6])
    with cols[0]:
        if o["pf"]: st.image(o["pf"], width=40)
    with cols[1]:
        st.markdown(f"**{o['name']}**")

if st.button("← 목록"):
    st.session_state.chat=None
    st.rerun()

# ================= MESSAGES =================
for m in chat["msgs"]:
    cls="me" if m["user"]==st.session_state.uid else "other"
    st.markdown(
        f"<div class='msg {cls}'>"
        f"<b>{users[m['user']]['name']}</b><br>"
        f"{m['text']}<br>"
        f"<span class='small'>❤️ {m['like']} {'✔✔' if len(m['read'])>1 else '✔'}</span>"
        f"</div>",unsafe_allow_html=True
    )

# ================= INPUT =================
txt=st.text_area("메시지")
img=st.file_uploader("이미지", type=["png","jpg","jpeg"])

if st.button("전송"):
    imgp=""
    if img:
        imgp=f"{UPLOAD_IMG}/{uuid.uuid4()}.png"
        open(imgp,"wb").write(img.read())

    chat["msgs"].append({
        "id":str(uuid.uuid4()),
        "user":st.session_state.uid,
        "text":txt,
        "img":imgp,
        "time":time.time(),
        "read":[st.session_state.uid],
        "like":0
    })
    save(CHATS,chats)
    st.rerun()

