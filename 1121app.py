import streamlit as st
import json, os, uuid, time

st.set_page_config(page_title="AOUSE CHAT", layout="centered")

DATA="data"
UPLOAD="uploads/profiles"
USERS=f"{DATA}/users.json"
CHATS=f"{DATA}/chats.json"

os.makedirs(DATA, exist_ok=True)
os.makedirs(UPLOAD, exist_ok=True)

def init(p,d):
    if not os.path.exists(p):
        json.dump(d, open(p,"w"), indent=2)

init(USERS,{})
init(CHATS,{})

def load(p): return json.load(open(p))
def save(p,d): json.dump(d,open(p,"w"),indent=2)

users=load(USERS)
chats=load(CHATS)

THEMES={
    "Pink":{"bg":"#ffe6f0","card":"#ffffff","me":"#ff5fa2","text":"#222"},
    "Blue":{"bg":"#eaf2ff","card":"#ffffff","me":"#6fa8ff","text":"#222"},
    "Mint":{"bg":"#ecfff8","card":"#ffffff","me":"#2dd4bf","text":"#222"},
    "Dark":{"bg":"#0f0f14","card":"#1c1c24","me":"#3b82f6","text":"#f5f5f5"},
    "Light":{"bg":"#f5f5f5","card":"#ffffff","me":"#999","text":"#222"},
    "Green":{"bg":"#ecfdf5","card":"#ffffff","me":"#22c55e","text":"#222"},
    "Yellow":{"bg":"#fffbe6","card":"#ffffff","me":"#facc15","text":"#222"}
}

# ================= SESSION =================
for k,v in {
    "uid":None,
    "page":"list",
    "chat":None
}.items():
    if k not in st.session_state:
        st.session_state[k]=v

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
theme=THEMES[me["theme"]]

# ================= STYLE =================
st.markdown(f"""
<style>
body {{ background:{theme['bg']}; color:{theme['text']}; }}
.app {{ max-width:420px;margin:auto; }}
.card {{
 background:{theme['card']};
 border-radius:20px;
 padding:14px;
 margin:8px 0;
 display:flex;
 align-items:center;
 gap:12px;
}}
.msg {{
 padding:12px;
 border-radius:18px;
 max-width:75%;
 margin:6px 0;
}}
.me {{ background:{theme['me']}; color:white; margin-left:auto; }}
.other {{ background:#eee; }}
.header {{
 display:flex;
 justify-content:space-between;
 align-items:center;
}}
.small {{ font-size:11px; opacity:.6; }}
.avatar {{
 width:42px;
 height:42px;
 border-radius:50%;
 object-fit:cover;
 background:#ddd;
}}
</style>
""", unsafe_allow_html=True)

# ================= SETTINGS =================
if st.session_state.page=="settings":
    st.markdown("## ⚙️ 내 프로필")

    if me["pf"]:
        st.image(me["pf"], width=80)

    pf=st.file_uploader("프로필 사진", type=["png","jpg","jpeg"])
    name=st.text_input("이름", me["name"])

    if pf:
        path=f"{UPLOAD}/{uuid.uuid4()}.png"
        open(path,"wb").write(pf.read())
        me["pf"]=path

    me["name"]=name
    me["theme"]=st.selectbox("테마", THEMES.keys(),
                              index=list(THEMES).index(me["theme"]))

    users[st.session_state.uid]=me
    save(USERS,users)

    if st.button("← 돌아가기"):
        st.session_state.page="list"
        st.rerun()
    st.stop()

# ================= HEADER =================
col1,col2=st.columns([8,1])
with col1:
    st.markdown("## 💬 채팅")
with col2:
    if st.button("⚙️"):
        st.session_state.page="settings"
        st.rerun()

# ================= FRIEND LIST =================
if st.session_state.page=="list":
    st.markdown("### 👥 친구")

    for uid,u in users.items():
        if uid==st.session_state.uid: continue
        cols=st.columns([1,6])
        with cols[0]:
            if u["pf"]: st.image(u["pf"], width=40)
        with cols[1]:
            if st.button(u["name"], key=uid):
                cid=str(uuid.uuid4())
                chats[cid]={
                    "members":[st.session_state.uid, uid],
                    "msgs":[]
                }
                save(CHATS,chats)
                st.session_state.chat=cid
                st.session_state.page="chat"
                st.rerun()

    if st.button("👥 그룹 채팅 만들기"):
        cid=str(uuid.uuid4())
        chats[cid]={
            "members":list(users.keys()),
            "msgs":[]
        }
        save(CHATS,chats)
        st.session_state.chat=cid
        st.session_state.page="chat"
        st.rerun()

    st.stop()

# ================= CHAT =================
chat=chats[st.session_state.chat]
members=[users[u] for u in chat["members"] if u!=st.session_state.uid]

cols=st.columns(len(members))
for i,m in enumerate(members):
    with cols[i]:
        if m["pf"]: st.image(m["pf"], width=40)
        st.caption(m["name"])

if st.button("← 목록"):
    st.session_state.page="list"
    st.rerun()

for m in chat["msgs"]:
    cls="me" if m["user"]==st.session_state.uid else "other"
    st.markdown(
        f"<div class='msg {cls}'><b>{users[m['user']]['name']}</b><br>{m['text']}</div>",
        unsafe_allow_html=True
    )

msg=st.text_area("메시지")
if st.button("전송"):
    chat["msgs"].append({
        "user":st.session_state.uid,
        "text":msg,
        "time":time.time()
    })
    save(CHATS,chats)
    st.rerun()
