import streamlit as st
import json, os, uuid, time

# ================= BASIC =================
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

# ================= SESSION =================
if "uid" not in st.session_state:
    st.session_state.uid=None
if "chat" not in st.session_state:
    st.session_state.chat=None
if "profile_view" not in st.session_state:
    st.session_state.profile_view=None

# ================= THEMES =================
THEMES={
    "핑크":"#ffd6e8",
    "블루":"#d6e9ff",
    "민트":"#d6fff2",
    "그린":"#e0ffd6",
    "옐로우":"#fff7cc",
    "라이트":"#ffffff",
    "다크":"#1e1e1e"
}

# ================= LOGIN =================
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

# ===== SAFETY =====
me.setdefault("name","USER")
me.setdefault("pf","")
me.setdefault("status","")
me.setdefault("theme","핑크")
save(USERS, users)

# ================= THEME =================
bg=THEMES.get(me["theme"],"#ffd6e8")
st.markdown(f"""
<style>
body {{ background:{bg}; }}
.chat {{ background:white; border-radius:15px; padding:10px; margin:6px 0; }}
.me {{ text-align:right; }}
.them {{ text-align:left; }}
.profile-box {{ text-align:center; }}
</style>
""", unsafe_allow_html=True)

# ================= PROFILE SETTINGS =================
with st.expander("⚙️ 프로필 설정"):
    col1,col2=st.columns([1,3])
    with col1:
        if me["pf"] and os.path.exists(me["pf"]):
            st.image(me["pf"], width=80)
        pf=st.file_uploader("프사", type=["png","jpg"], key="pf")
        if pf:
            path=f"{UPLOAD}/{st.session_state.uid}.png"
            open(path,"wb").write(pf.read())
            me["pf"]=path
            save(USERS, users)
            st.rerun()
    with col2:
        me["name"]=st.text_input("이름", me["name"])
        me["status"]=st.text_input("상태메시지", me["status"])
        me["theme"]=st.selectbox("테마", THEMES, index=list(THEMES).index(me["theme"]))
        if st.button("저장"):
            save(USERS, users)

# ================= CHAT LIST =================
st.markdown("### 💬 채팅")

def chat_title(c):
    if c["type"]=="group": return c["name"]
    other=[u for u in c["members"] if u!=st.session_state.uid][0]
    return users[other]["name"]

def chat_status(c):
    if c["type"]=="group": return "그룹 채팅"
    other=[u for u in c["members"] if u!=st.session_state.uid][0]
    return users[other]["status"]

for cid,c in chats.items():
    if st.button(f"{chat_title(c)}\n{chat_status(c)}", key=cid):
        st.session_state.chat=cid

# ================= CREATE GROUP =================
with st.expander("➕ 그룹 채팅"):
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

# ================= CHAT VIEW =================
if not st.session_state.chat: st.stop()

cid=st.session_state.chat
chat=chats[cid]

# ===== 상대 프로필 상단 =====
if chat["type"]=="private":
    other=[u for u in chat["members"] if u!=st.session_state.uid][0]
    if st.button("프로필 보기"):
        st.session_state.profile_view=other

    if users[other]["pf"]:
        st.image(users[other]["pf"], width=80)
    st.markdown(f"**{users[other]['name']}**")
    st.caption(users[other]["status"])
else:
    st.markdown(f"### 👥 {chat['name']}")

# ===== 프로필 상세 페이지 =====
if st.session_state.profile_view:
    u=users[st.session_state.profile_view]
    st.markdown("---")
    if u["pf"]: st.image(u["pf"], width=120)
    st.markdown(f"### {u['name']}")
    st.caption(u["status"])
    if st.button("닫기"):
        st.session_state.profile_view=None
        st.rerun()

# ================= MESSAGES =================
for m in messages[cid]:
    cls="me" if m["uid"]==st.session_state.uid else "them"
    st.markdown(f"""
    <div class="chat {cls}">
    <b>{users[m["uid"]]["name"]}</b><br>
    {m["text"]}
    </div>
    """, unsafe_allow_html=True)

# ================= SEND =================
msg=st.text_area("메시지", height=80)
if st.button("전송") and msg:
    messages[cid].append({
        "uid":st.session_state.uid,
        "text":msg,
        "time":time.time()
    })
    save(MESSAGES,messages)
    st.rerun()


