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

# ================= THEME (확장 가능) =================
THEMES={
 "Pink":{
    "bg":"#ffe6f0","card":"#ffffff","me":"#ff5fa2",
    "btn":"#ff8fc7","text":"#222"
 },
 "Blue":{
    "bg":"#eaf4ff","card":"#ffffff","me":"#6fa8ff",
    "btn":"#8fbaff","text":"#222"
 },
 "Dark":{
    "bg":"#0f0f14","card":"#1c1c24","me":"#3b82f6",
    "btn":"#2d2d3a","text":"#f5f5f5"
 },
 "Cream":{
    "bg":"#fff7ec","card":"#ffffff","me":"#f4a261",
    "btn":"#ffd6a5","text":"#222"
 },
 "Mint":{
    "bg":"#ecfff8","card":"#ffffff","me":"#2dd4bf",
    "btn":"#99f6e4","text":"#222"
 }
}

# ================= SESSION =================
for k in ["uid","chat"]:
    if k not in st.session_state:
        st.session_state[k]=None

# ================= LOGIN =================
if not st.session_state.uid:
    st.markdown("## 💬 AOUSE CHAT")
    name=st.text_input("이름")
    theme=st.selectbox("테마 선택", THEMES.keys())
    if st.button("시작"):
        uid=str(uuid.uuid4())
        users[uid]={"name":name,"theme":theme}
        save(USERS,users)
        st.session_state.uid=uid
        st.rerun()
    st.stop()

me=users[st.session_state.uid]
theme=THEMES[me["theme"]]

# ================= STYLE =================
st.markdown(f"""
<style>
body {{
 background:{theme['bg']};
 color:{theme['text']};
}}
.app {{ max-width:420px;margin:auto; }}
.card {{
 background:{theme['card']};
 border-radius:22px;
 padding:16px;
 margin:10px 0;
 box-shadow:0 10px 30px rgba(0,0,0,.08);
}}
.msg {{
 padding:14px;
 border-radius:22px;
 max-width:80%;
 margin:6px 0;
 word-break:break-word;
}}
.me {{
 background:{theme['me']};
 color:white;
 margin-left:auto;
}}
.other {{
 background:{theme['card']};
}}
.btn {{
 background:{theme['btn']};
 color:white;
 border-radius:14px;
 padding:8px 12px;
}}
.small {{ font-size:11px;opacity:.6; }}
</style>
""", unsafe_allow_html=True)

# ================= PROFILE =================
with st.sidebar:
    st.subheader("👤 프로필")
    me["name"]=st.text_input("이름",me["name"])
    me["theme"]=st.selectbox(
        "테마",
        THEMES.keys(),
        index=list(THEMES).index(me["theme"])
    )
    users[st.session_state.uid]=me
    save(USERS,users)

# ================= CHAT LIST =================
if not st.session_state.chat:
    st.markdown("## 💬 채팅")

    if st.button("➕ 1:1 채팅"):
        cid=str(uuid.uuid4())
        chats[cid]={
            "name":"1:1 채팅",
            "members":[st.session_state.uid],
            "msgs":[],
            "pin":False,
            "group":False
        }
        save(CHATS,chats)

    if st.button("👥 그룹 채팅"):
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

cols=st.columns([5,1,1])
cols[0].markdown(f"### {'👥 ' if chat['group'] else ''}{chat['name']}")
if cols[1].button("📌"):
    chat["pin"]=not chat["pin"]
    save(CHATS,chats)
    st.rerun()
if cols[2].button("🗑"):
    del chats[cid]
    save(CHATS,chats)
    st.session_state.chat=None
    st.rerun()

if st.button("← 목록"):
    st.session_state.chat=None
    st.rerun()

# ================= MESSAGES =================
for m in chat["msgs"]:
    cls="me" if m["user"]==st.session_state.uid else "other"
    if st.session_state.uid not in m["read"]:
        m["read"].append(st.session_state.uid)
        save(CHATS,chats)

    st.markdown(
        f"<div class='msg {cls}'>"
        f"<b>{users[m['user']]['name']}</b><br>"
        f"{'삭제된 메시지' if m['del'] else m['text']}"
        f"<br><span class='small'>"
        f"{'❤️ '+str(m['like']) if m['like']>0 else ''} "
        f"{'✔✔' if len(m['read'])>1 else '✔'}"
        f"</span></div>",
        unsafe_allow_html=True
    )

    if not m["del"]:
        c1,c2=st.columns(2)
        if c1.button("❤️", key=m["id"]+"l"):
            m["like"]+=1
            save(CHATS,chats)
            st.rerun()
        if m["user"]==st.session_state.uid:
            if c2.button("삭제", key=m["id"]+"d"):
                m["del"]=True
                save(CHATS,chats)
                st.rerun()

# ================= INPUT =================
msg=st.text_area("메시지 입력")

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

