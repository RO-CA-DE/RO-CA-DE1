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
 "Pink":{"bg":"#ffe6f0","me":"#ff5fa2"},
 "Blue":{"bg":"#eaf2ff","me":"#6fa8ff"},
 "Mint":{"bg":"#ecfff8","me":"#2dd4bf"},
 "Dark":{"bg":"#0f0f14","me":"#3b82f6"},
 "Light":{"bg":"#f5f5f5","me":"#999"},
 "Green":{"bg":"#ecfdf5","me":"#22c55e"},
 "Yellow":{"bg":"#fffbe6","me":"#facc15"}
}

# ================= SESSION =================
for k,v in {
    "uid":None,
    "tab":"friends",
    "chat":None,
    "typing":False
}.items():
    if k not in st.session_state:
        st.session_state[k]=v

# ================= AUTO REFRESH =================
st.experimental_set_query_params(t=int(time.time()))
time.sleep(1)

# ================= LOGIN =================
if not st.session_state.uid:
    st.markdown("## 💬 AOUSE CHAT")
    name=st.text_input("이름")
    if st.button("시작"):
        uid=str(uuid.uuid4())
        users[uid]={"name":name,"pf":"","theme":"Pink"}
        save(USERS,users)
        st.session_state.uid=uid
        st.rerun()
    st.stop()

me=users[st.session_state.uid]
theme=THEMES[me["theme"]]

st.markdown(
    f"<style>body{{background:{theme['bg']};}}</style>",
    unsafe_allow_html=True
)

# ================= HEADER =================
st.markdown("## 💬 AOUSE")

# ================= CHAT VIEW =================
if st.session_state.chat:
    chat=chats[st.session_state.chat]

    others=[u for u in chat["members"] if u!=st.session_state.uid]
    st.markdown(" ".join([f"👤 {users[o]['name']}" for o in others]))

    for m in chat["msgs"]:
        if st.session_state.uid not in m["read"]:
            m["read"].append(st.session_state.uid)
            save(CHATS,chats)

        read="✔✔" if len(m["read"])>1 else "✔"
        txt="삭제된 메시지" if m["deleted"] else m["text"]

        st.markdown(
            f"**{users[m['user']]['name']}**: {txt} ❤️{m['like']} {read}"
        )

        if m["user"]==st.session_state.uid and not m["deleted"]:
            if st.button("🗑 삭제", key=m["id"]):
                m["deleted"]=True
                save(CHATS,chats)
                st.rerun()
            if st.button("❤️", key=m["id"]+"l"):
                m["like"]+=1
                save(CHATS,chats)
                st.rerun()

    txt=st.text_input("메시지 입력", on_change=lambda: st.session_state.update({"typing":True}))
    if st.button("전송"):
        chat["msgs"].append({
            "id":str(uuid.uuid4()),
            "user":st.session_state.uid,
            "text":txt,
            "time":time.time(),
            "read":[st.session_state.uid],
            "like":0,
            "deleted":False
        })
        st.session_state.typing=False
        save(CHATS,chats)
        st.rerun()

    if st.button("← 뒤로"):
        st.session_state.chat=None
        st.rerun()

# ================= FRIENDS =================
elif st.session_state.tab=="friends":
    st.markdown("### 👥 친구")
    for uid,u in users.items():
        if uid==st.session_state.uid: continue
        if st.button(u["name"], key=uid):
            cid=str(uuid.uuid4())
            chats[cid]={"members":[st.session_state.uid,uid],"msgs":[]}
            save(CHATS,chats)
            st.session_state.chat=cid
            st.rerun()

# ================= SETTINGS =================
elif st.session_state.tab=="settings":
    st.markdown("### ⚙️ 설정")
    me["name"]=st.text_input("이름", me["name"])
    me["theme"]=st.selectbox("테마", THEMES.keys(),
        index=list(THEMES).index(me["theme"]))
    save(USERS,users)

# ================= BOTTOM TAB =================
st.markdown("---")
c1,c2,c3=st.columns(3)
with c1:
    if st.button("🏠"):
        st.session_state.tab="friends"
        st.session_state.chat=None
        st.rerun()
with c2:
    if st.button("💬"):
        st.session_state.tab="friends"
        st.rerun()
with c3:
    if st.button("⚙️"):
        st.session_state.tab="settings"
        st.session_state.chat=None
        st.rerun()
