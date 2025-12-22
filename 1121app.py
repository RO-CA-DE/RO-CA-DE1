import streamlit as st
import json, os, uuid, time

# ================= BASIC =================
st.set_page_config(page_title="AOUSE CHAT", layout="centered")

DATA="data"
USERS=f"{DATA}/users.json"
CHATS=f"{DATA}/chats.json"
os.makedirs(DATA, exist_ok=True)

for f in [USERS, CHATS]:
    if not os.path.exists(f):
        with open(f,"w") as fp:
            json.dump({}, fp)

def load(p):
    with open(p) as f: return json.load(f)

def save(p,d):
    with open(p,"w") as f: json.dump(d,f,indent=2)

users = load(USERS)
chats = load(CHATS)

# ================= THEME =================
THEMES={
 "pink":{"bg":"#ffe6f0","me":"#ff5fa2"},
 "blue":{"bg":"#eaf4ff","me":"#6fa8ff"},
 "dark":{"bg":"#111","me":"#333"}
}

# ================= SESSION =================
for k in ["uid","chat","typing"]:
    if k not in st.session_state:
        st.session_state[k]=None

# ================= LOGIN =================
if not st.session_state.uid:
    st.markdown("## 💬 AOUSE CHAT")
    name=st.text_input("이름")
    theme=st.selectbox("테마", THEMES)
    if st.button("시작"):
        uid=str(uuid.uuid4())
        users[uid]={
            "name":name,
            "theme":theme,
            "last":0
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
body {{ background:{theme['bg']}; }}
.app {{ max-width:420px;margin:auto; }}
.card {{
 background:white;
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
.me {{ background:{theme['me']};color:white;margin-left:auto; }}
.other {{ background:white; }}
.small {{ font-size:11px;opacity:.6; }}
.pin {{ color:#ff5fa2;font-weight:bold; }}
</style>
""", unsafe_allow_html=True)

# ================= PROFILE =================
with st.sidebar:
    st.subheader("👤 프로필")
    me["name"]=st.text_input("이름",me["name"])
    me["theme"]=st.selectbox(
        "테마",THEMES,
        index=list(THEMES).index(me["theme"])
    )
    users[st.session_state.uid]=me
    save(USERS,users)

# ================= CHAT LIST =================
if not st.session_state.chat:
    st.markdown("## 💬 채팅 목록")

    if st.button("➕ 새 채팅"):
        cid=str(uuid.uuid4())
        chats[cid]={
            "name":"1:1 채팅",
            "members":[st.session_state.uid],
            "msgs":[],
            "pin":False,
            "group":False
        }
        save(CHATS,chats)

    if st.button("👥 그룹 채팅 생성"):
        cid=str(uuid.uuid4())
        chats[cid]={
            "name":"그룹 채팅",
            "members":[st.session_state.uid],
            "msgs":[],
            "pin":False,
            "group":True
        }
        save(CHATS,chats)

    def sort_key(item):
        last=item[1]["msgs"][-1]["time"] if item[1]["msgs"] else 0
        return (not item[1]["pin"], -last)

    for cid,c in sorted(chats.items(), key=sort_key):
        if st.session_state.uid in c["members"]:
            unread=sum(
                1 for m in c["msgs"]
                if st.session_state.uid not in m["read"]
            )
            label=f"{'📌 ' if c['pin'] else ''}{'👥 ' if c['group'] else ''}{c['name']}"
            if unread>0: label+=f" 🔔 {unread}"
            if st.button(label, key=cid):
                st.session_state.chat=cid
                st.rerun()
    st.stop()

# ================= CHAT ROOM =================
cid=st.session_state.chat
chat=chats[cid]

st.markdown(f"### {'👥 ' if chat['group'] else ''}{chat['name']}")

cols=st.columns(3)
if cols[0].button("📌"):
    chat["pin"]=not chat["pin"]
    save(CHATS,chats)
    st.rerun()

if cols[1].button("← 목록"):
    st.session_state.chat=None
    st.rerun()

if cols[2].button("🗑"):
    del chats[cid]
    save(CHATS,chats)
    st.session_state.chat=None
    st.rerun()

# ================= MESSAGES =================
for m in chat["msgs"]:
    cls="me" if m["user"]==st.session_state.uid else "other"
    if st.session_state.uid not in m["read"]:
        m["read"].append(st.session_state.uid)
        save(CHATS,chats)

    name=users[m["user"]]["name"]
    st.markdown(
        f"<div class='msg {cls}'>"
        f"<b>{name}</b><br>"
        f"{'삭제된 메시지' if m['del'] else m['text']}"
        f"<br><span class='small'>"
        f"{'❤️ '+str(m['like']) if m['like']>0 else ''} "
        f"{'✔✔' if len(m['read'])>1 else '✔'}"
        f"</span></div>",
        unsafe_allow_html=True
    )

    if not m["del"]:
        cols=st.columns(2)
        if cols[0].button("❤️", key=m["id"]+"l"):
            m["like"]+=1
            save(CHATS,chats)
            st.rerun()
        if m["user"]==st.session_state.uid:
            if cols[1].button("삭제", key=m["id"]+"d"):
                m["del"]=True
                save(CHATS,chats)
                st.rerun()

# ================= INPUT =================
msg=st.text_area("메시지")

if msg:
    st.caption("입력중…")

if st.button("전송"):
    chat["msgs"].append({
        "id":str(uuid.uuid4()),
        "user":st.session_state.uid,
        "text":msg,
        "time":time.time(),
        "read":[st.session_state.uid],
        "like":0,
        "del":False
    })
    save(CHATS,chats)
    st.rerun()
