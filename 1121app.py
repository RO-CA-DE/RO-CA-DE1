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
    if os.path.exists(p):
        try:
            return json.load(open(p, encoding="utf-8"))
        except:
            return d
    return d

def save(p, d):
    json.dump(d, open(p,"w",encoding="utf-8"), ensure_ascii=False, indent=2)

users = load(USERS,{})
chats = load(CHATS,{})
messages = load(MESSAGES,{})

# ================= SESSION =================
if "uid" not in st.session_state:
    st.session_state.uid=None
if "chat" not in st.session_state:
    st.session_state.chat=None
if "profile_view" not in st.session_state:
    st.session_state.profile_view=None

# ================= LOGIN =================
st.markdown("## 💬 CHAT")

if not st.session_state.uid:
    name = st.text_input("이름")
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

# ================= USER SAFETY =================
me = users.get(st.session_state.uid, {})
me.setdefault("name","USER")
me.setdefault("pf","")
me.setdefault("status","")
me.setdefault("theme","핑크")
users[st.session_state.uid]=me
save(USERS, users)

# ================= CHAT SAFETY =================
for cid,c in chats.items():
    if not isinstance(c, dict):
        chats[cid]={}
        c=chats[cid]

    c.setdefault("type","private")
    c.setdefault("members",[])
    if c["type"]=="group":
        c.setdefault("name","그룹 채팅")
        c.setdefault("admin", c["members"][0] if c["members"] else "")

    messages.setdefault(cid, [])

save(CHATS,chats)
save(MESSAGES,messages)

# ================= THEME =================
THEMES={
    "핑크":"#ffd6e8",
    "블루":"#d6e9ff",
    "민트":"#d6fff2",
    "그린":"#e0ffd6",
    "옐로우":"#fff7cc",
    "라이트":"#ffffff",
    "다크":"#1e1e1e"
}
bg = THEMES.get(me["theme"],"#ffd6e8")

st.markdown(f"""
<style>
body {{ background:{bg}; }}
.chat {{ background:white; border-radius:15px; padding:10px; margin:6px 0; }}
.me {{ text-align:right; }}
.them {{ text-align:left; }}
.profile {{ text-align:center; }}
</style>
""", unsafe_allow_html=True)

# ================= PROFILE SETTINGS =================
with st.expander("⚙️ 프로필 설정"):
    col1,col2=st.columns([1,3])
    with col1:
        if me["pf"] and os.path.exists(me["pf"]):
            st.image(me["pf"], width=80)
        pf=st.file_uploader("프사", type=["png","jpg","jpeg"])
        if pf:
            path=f"{UPLOAD}/{st.session_state.uid}.png"
            with open(path,"wb") as f:
                f.write(pf.read())
            me["pf"]=path
            save(USERS, users)
            st.rerun()
    with col2:
        me["name"]=st.text_input("이름", me["name"])
        me["status"]=st.text_input("상태메시지", me["status"])
        me["theme"]=st.selectbox("테마", THEMES.keys(), index=list(THEMES).index(me["theme"]))
        if st.button("저장"):
            save(USERS, users)

# ================= CHAT LIST =================
st.markdown("### 💬 채팅 목록")

def chat_title(c):
    if c.get("type")=="group":
        return c.get("name","그룹 채팅")
    members=c.get("members",[])
    other=[u for u in members if u!=st.session_state.uid]
    return users.get(other[0],{}).get("name","채팅") if other else "채팅"

def chat_status(c):
    if c.get("type")=="group":
        return "그룹 채팅"
    members=c.get("members",[])
    other=[u for u in members if u!=st.session_state.uid]
    return users.get(other[0],{}).get("status","") if other else ""

for cid,c in chats.items():
    if st.button(f"{chat_title(c)}\n{chat_status(c)}", key=f"chat_{cid}"):
        st.session_state.chat=cid

# ================= CREATE GROUP =================
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

# ================= CHAT VIEW =================
if not st.session_state.chat:
    st.stop()

cid=st.session_state.chat
chat=chats[cid]

# ===== 상단 프로필 =====
if chat.get("type")=="private":
    members=chat.get("members",[])
    other=[u for u in members if u!=st.session_state.uid]
    if other:
        u=users.get(other[0],{})
        if st.button("프로필 보기"):
            st.session_state.profile_view=other[0]
        if u.get("pf"):
            st.image(u["pf"], width=90)
        st.markdown(f"### {u.get('name','')}")
        st.caption(u.get("status",""))
else:
    st.markdown(f"## 👥 {chat.get('name')}")

# ===== 프로필 상세 =====
if st.session_state.profile_view:
    u=users.get(st.session_state.profile_view,{})
    st.markdown("---")
    if u.get("pf"):
        st.image(u["pf"], width=140)
    st.markdown(f"### {u.get('name','')}")
    st.caption(u.get("status",""))
    if st.button("닫기"):
        st.session_state.profile_view=None
        st.rerun()

# ================= MESSAGES =================
for m in messages.get(cid,[]):
    cls="me" if m.get("uid")==st.session_state.uid else "them"
    st.markdown(f"""
    <div class="chat {cls}">
    <b>{users.get(m.get("uid"),{}).get("name","")}</b><br>
    {m.get("text","")}
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



