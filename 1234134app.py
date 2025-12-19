import streamlit as st
import json, os
from datetime import datetime

# ================= CONFIG =================
st.set_page_config("BLUSH", layout="centered")

DATA="data"
os.makedirs(DATA, exist_ok=True)

USERS=f"{DATA}/users.json"
CHATS=f"{DATA}/chats.json"

def load(p):
    if not os.path.exists(p):
        with open(p,"w",encoding="utf-8") as f:
            json.dump({},f)
    with open(p,encoding="utf-8") as f:
        return json.load(f)

def save(p,d):
    with open(p,"w",encoding="utf-8") as f:
        json.dump(d,f,ensure_ascii=False,indent=2)

users=load(USERS)
chats=load(CHATS)

# ================= STYLE =================
st.markdown("""
<style>
body {background:#fff0f6;}
h1 {color:#ff4d8d;text-align:center;}
.card {
 background:white;
 padding:18px;
 border-radius:22px;
 box-shadow:0 10px 30px rgba(255,105,180,.18);
 margin-bottom:14px;
}
.chat-left {
 background:#ffe0ec;
 padding:10px 14px;
 border-radius:18px 18px 18px 4px;
 margin:6px 0;
 width:fit-content;
}
.chat-right {
 background:#ff7eb3;
 color:white;
 padding:10px 14px;
 border-radius:18px 18px 4px 18px;
 margin:6px 0 6px auto;
 width:fit-content;
}
.badge {
 background:#ff4d8d;
 color:white;
 padding:2px 8px;
 border-radius:10px;
 font-size:11px;
 margin-left:6px;
}
button {
 background:linear-gradient(135deg,#ff7eb3,#ff4d8d)!important;
 color:white!important;
 border-radius:20px!important;
 border:none!important;
}
</style>
""",unsafe_allow_html=True)

# ================= SESSION =================
if "user" not in st.session_state: st.session_state.user=None
if "chat_with" not in st.session_state: st.session_state.chat_with=None

# ================= HELPERS =================
def room_id(a,b):
    return "_".join(sorted([a,b]))

def unread(me):
    c=0
    for r in chats.values():
        if me in r["users"]:
            for m in r["messages"]:
                if m["user"]!=me and me not in m.get("read",[]):
                    c+=1
    return c

# ================= AUTH =================
st.title("💗 BLUSH")

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
                users[nid]={}
                save(USERS,users)
                st.success("Account created!")
    st.stop()

me=st.session_state.user

# ================= HEADER =================
u=unread(me)
st.markdown(
    f"<div class='card'><b>@{me}</b> "
    f"{'🔴 '+str(u) if u else ''}</div>",
    unsafe_allow_html=True
)

# ================= USER LIST =================
st.subheader("💬 Chats")
for u in users:
    if u==me: continue
    rid=room_id(me,u)
    chats.setdefault(rid,{"users":[me,u],"messages":[]})

    unread_here=sum(
        1 for m in chats[rid]["messages"]
        if m["user"]!=me and me not in m.get("read",[])
    )

    label=f"@{u}"
    if unread_here: label+=f" 🔴{unread_here}"

    if st.button(label):
        st.session_state.chat_with=u

# ================= CHAT ROOM =================
if st.session_state.chat_with:
    other=st.session_state.chat_with
    rid=room_id(me,other)
    room=chats[rid]

    st.markdown("---")
    st.markdown(f"### 💗 Chat with @{other}")

    for m in room["messages"]:
        m.setdefault("read",[])
        if me not in m["read"]:
            m["read"].append(me)

        cls="chat-right" if m["user"]==me else "chat-left"
        st.markdown(
            f"<div class='{cls}'>{m['text']}<br>"
            f"<small>{m['time']}</small></div>",
            unsafe_allow_html=True
        )

    with st.form("send"):
        msg=st.text_input("Message")
        if st.form_submit_button("Send"):
            room["messages"].append({
                "user":me,
                "text":msg,
                "time":datetime.now().strftime("%H:%M"),
                "read":[me]
            })
            save(CHATS,chats)
            st.rerun()

save(CHATS,chats)
