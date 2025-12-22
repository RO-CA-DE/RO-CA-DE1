import streamlit as st
import json, os, uuid, time

st.set_page_config(page_title="AOUSE CHAT", layout="centered")

DATA="data"
UPLOAD="uploads/profiles"
USERS=f"{DATA}/users.json"
CHATS=f"{DATA}/chats.json"
THEMES=f"{DATA}/themes.json"

os.makedirs(DATA, exist_ok=True)
os.makedirs(UPLOAD, exist_ok=True)

def init(p,d):
    if not os.path.exists(p):
        json.dump(d, open(p,"w"), indent=2)

init(USERS,{})
init(CHATS,{})
init(THEMES,{
    "Pink":{"bg":"#ffe6f0","card":"#ffffff","me":"#ff5fa2","text":"#222"},
    "Dark":{"bg":"#111111","card":"#1c1c1c","me":"#3b82f6","text":"#f5f5f5"}
})

def load(p): return json.load(open(p))
def save(p,d): json.dump(d,open(p,"w"),indent=2)

users=load(USERS)
chats=load(CHATS)
themes=load(THEMES)

# ================= SESSION =================
if "uid" not in st.session_state: st.session_state.uid=None
if "page" not in st.session_state: st.session_state.page="list"
if "chat" not in st.session_state: st.session_state.chat=None

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
theme=themes[me["theme"]]

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
 display:flex; justify-content:space-between; align-items:center;
}}
.small {{ font-size:11px; opacity:.6; }}
</style>
""", unsafe_allow_html=True)

# ================= SETTINGS PAGE =================
if st.session_state.page=="settings":
    st.markdown("## ⚙️ 프로필 설정")

    if me["pf"]:
        st.image(me["pf"], width=90)

    pf=st.file_uploader("프로필 사진", type=["png","jpg"])
    name=st.text_input("이름", me["name"])

    if pf:
        path=f"{UPLOAD}/{uuid.uuid4()}.png"
        open(path,"wb").write(pf.read())
        me["pf"]=path

    me["name"]=name
    users[st.session_state.uid]=me
    save(USERS,users)

    st.markdown("### 🎨 테마 선택")
    me["theme"]=st.selectbox(
        "기존 테마",
        list(themes.keys()),
        index=list(themes.keys()).index(me["theme"])
    )
    save(USERS,users)

    st.markdown("### ➕ 테마 추가 (항상 보임)")
    tname=st.text_input("테마 이름")
    bg=st.color_picker("배경")
    card=st.color_picker("카드")
    bubble=st.color_picker("내 말풍선")
    txt=st.color_picker("텍스트")

    if st.button("➕ 테마 추가 & 적용"):
        if tname:
            themes[tname]={
                "bg":bg,"card":card,"me":bubble,"text":txt
            }
            save(THEMES,themes)
            me["theme"]=tname
            save(USERS,users)
            st.success("테마 적용 완료")

    if st.button("← 돌아가기"):
        st.session_state.page="list"
        st.rerun()

    st.stop()

# ================= HEADER =================
st.markdown(
    f"<div class='header'><h3>💬 채팅</h3></div>",
    unsafe_allow_html=True
)

if st.button("⚙️ 설정"):
    st.session_state.page="settings"
    st.rerun()

# ================= CHAT LIST =================
if st.session_state.page=="list":
    if st.button("➕ 새 채팅"):
        cid=str(uuid.uuid4())
        chats[cid]={
            "members":[st.session_state.uid],
            "msgs":[]
        }
        save(CHATS,chats)

    for cid,c in chats.items():
        if st.session_state.uid in c["members"]:
            if st.button("채팅방", key=cid):
                st.session_state.chat=cid
                st.session_state.page="chat"
                st.rerun()
    st.stop()

# ================= CHAT PAGE =================
chat=chats[st.session_state.chat]

# 상대 프로필 표시
others=[u for u in chat["members"] if u!=st.session_state.uid]
if others:
    o=users[others[0]]
    cols=st.columns([1,6])
    with cols[0]:
        if o["pf"]: st.image(o["pf"], width=40)
    with cols[1]:
        st.markdown(f"**{o['name']}**")

if st.button("← 목록"):
    st.session_state.page="list"
    st.rerun()

# 메시지
for m in chat["msgs"]:
    cls="me" if m["user"]==st.session_state.uid else "other"
    st.markdown(
        f"<div class='msg {cls}'>{users[m['user']]['name']}<br>{m['text']}</div>",
        unsafe_allow_html=True
    )

txt=st.text_area("메시지")
if st.button("전송"):
    chat["msgs"].append({
        "user":st.session_state.uid,
        "text":txt,
        "time":time.time()
    })
    save(CHATS,chats)
    st.rerun()


