import streamlit as st
import json, os, uuid, time
from datetime import datetime

# ================== BASIC ==================
st.set_page_config(page_title="CHAT", layout="centered")

DATA="data"
UPLOAD="uploads"
os.makedirs(DATA, exist_ok=True)
os.makedirs(UPLOAD, exist_ok=True)

USERS=f"{DATA}/users.json"
CHATS=f"{DATA}/chats.json"
MESSAGES=f"{DATA}/messages.json"

def load(p, d): 
    return json.load(open(p)) if os.path.exists(p) else d

def save(p, d): 
    json.dump(d, open(p,"w"), ensure_ascii=False, indent=2)

users=load(USERS,{})
chats=load(CHATS,{})
messages=load(MESSAGES,{})

# ================== SESSION ==================
if "uid" not in st.session_state:
    st.session_state.uid=None
if "chat" not in st.session_state:
    st.session_state.chat=None

# ================== THEMES ==================
THEMES={
    "핑크":"#ffd6e8",
    "블루":"#d6e9ff",
    "민트":"#d6fff2",
    "그린":"#e0ffd6",
    "옐로우":"#fff7cc",
    "라이트":"#ffffff",
    "다크":"#1e1e1e"
}

# ================== LOGIN ==================
st.markdown("## 💬 CHAT")

if not st.session_state.uid:
    name=st.text_input("이름")
    if st.button("로그인") and name:
        uid=str(uuid.uuid4())
        users[uid]={
            "name":name,
            "pf":"",
            "status":"",
            "theme":"핑크"
        }
        save(USERS, users)
        st.session_state.uid=uid
        st.rerun()
    st.stop()

me=users[st.session_state.uid]

# ================== THEME APPLY ==================
bg=THEMES.get(me["theme"],"#ffd6e8")
st.markdown(f"""
<style>
body {{
 background:{bg};
}}
.chat {{
 background:white;
 border-radius:15px;
 padding:10px;
 margin:5px 0;
}}
.me {{ text-align:right; }}
.them {{ text-align:left; }}
</style>
""", unsafe_allow_html=True)

# ================== PROFILE ==================
with st.expander("⚙️ 프로필 설정"):
    me["name"]=st.text_input("이름", me["name"])
    me["status"]=st.text_input("상태메시지", me["status"])
    pf=st.file_uploader("프로필 이미지", type=["png","jpg"])
    if pf:
        path=f"{UPLOAD}/{uuid.uuid4()}.png"
        open(path,"wb").write(pf.read())
        me["pf"]=path
    me["theme"]=st.selectbox("테마", THEMES.keys(), index=list(THEMES).index(me["theme"]))
    save(USERS, users)

# ================== CHAT LIST ==================
st.markdown("### 💬 채팅 목록")

def chat_title(c):
    if c["type"]=="group": return c["name"]
    other=[u for u in c["members"] if u!=st.session_state.uid][0]
    return users[other]["name"]

for cid,c in chats.items():
    col1,col2=st.columns([4,1])
    with col1:
        if st.button(chat_title(c), key=cid):
            st.session_state.chat=cid
    with col2:
        if st.button("📌" if not c.get("pin") else "❌", key=f"p{cid}"):
            c["pin"]=not c.get("pin")
            save(CHATS, chats)

# ================== CREATE GROUP ==================
with st.expander("➕ 그룹 채팅 만들기"):
    gname=st.text_input("방 이름")
    members=st.multiselect(
        "멤버",
        [u for u in users if u!=st.session_state.uid],
        format_func=lambda x: users[x]["name"]
    )
    if st.button("생성") and gname:
        cid=str(uuid.uuid4())
        chats[cid]={
            "type":"group",
            "name":gname,
            "members":[st.session_state.uid]+members,
            "admin":st.session_state.uid
        }
        messages[cid]=[]
        save(CHATS,chats)
        save(MESSAGES,messages)
        st.session_state.chat=cid
        st.rerun()

# ================== CHAT VIEW ==================
if not st.session_state.chat: st.stop()

cid=st.session_state.chat
chat=chats[cid]

st.markdown(f"## {chat_title(chat)}")

# ===== 멤버 표시 (에러 방지) =====
others=[u for u in chat["members"] if u!=st.session_state.uid]
if len(others)>0:
    cols=st.columns(len(others))
    for i,u in enumerate(others):
        with cols[i]:
            if users[u]["pf"]: st.image(users[u]["pf"], width=40)
            st.caption(users[u]["name"])
else:
    st.caption("👤 혼자 있는 채팅")

# ===== 방 관리 =====
if chat["type"]=="group" and chat["admin"]==st.session_state.uid:
    new=st.text_input("방 이름 변경", chat["name"])
    if st.button("변경"):
        chat["name"]=new
        save(CHATS,chats)
    if st.button("방 삭제"):
        chats.pop(cid)
        messages.pop(cid)
        save(CHATS,chats); save(MESSAGES,messages)
        st.session_state.chat=None
        st.rerun()

# ================== MESSAGES ==================
for m in messages[cid]:
    cls="me" if m["uid"]==st.session_state.uid else "them"
    st.markdown(f"""
    <div class="chat {cls}">
    <b>{users[m["uid"]]["name"]}</b><br>
    {m["text"]}
    </div>
    """, unsafe_allow_html=True)

# ================== SEND ==================
txt=st.text_area("메시지", key="msg", height=80)
img=st.file_uploader("이미지", type=["png","jpg"])
if st.button("전송"):
    messages[cid].append({
        "uid":st.session_state.uid,
        "text":txt,
        "time":time.time()
    })
    save(MESSAGES,messages)
    st.session_state.msg=""
    st.rerun()

