import streamlit as st
import json, os, uuid, time
from PIL import Image

# ================= BASIC =================
st.set_page_config(page_title="AOUSE CHAT", layout="centered")

DATA="data"
UPLOAD="uploads/images"
USERS=f"{DATA}/users.json"
CHATS=f"{DATA}/chats.json"
THEMES_FILE=f"{DATA}/themes.json"
os.makedirs(DATA, exist_ok=True)
os.makedirs(UPLOAD, exist_ok=True)

for f,default in [
    (USERS,{}),
    (CHATS,{}),
    (THEMES_FILE,{
        "Pink":{"bg":"#ffe6f0","card":"#ffffff","me":"#ff5fa2","btn":"#ff8fc7","text":"#222"},
        "Blue":{"bg":"#eaf4ff","card":"#ffffff","me":"#6fa8ff","btn":"#8fbaff","text":"#222"},
        "Dark":{"bg":"#0f0f14","card":"#1c1c24","me":"#3b82f6","btn":"#2d2d3a","text":"#f5f5f5"},
        "Cream":{"bg":"#fff7ec","card":"#ffffff","me":"#f4a261","btn":"#ffd6a5","text":"#222"},
        "Mint":{"bg":"#ecfff8","card":"#ffffff","me":"#2dd4bf","btn":"#99f6e4","text":"#222"}
    })
]:
    if not os.path.exists(f):
        with open(f,"w") as fp:
            json.dump(default, fp, indent=2)

def load(p): 
    with open(p) as f: return json.load(f)
def save(p,d):
    with open(p,"w") as f: json.dump(d,f,indent=2)

users = load(USERS)
chats = load(CHATS)
themes = load(THEMES_FILE)

# ================= SESSION =================
for k in ["uid","chat"]:
    if k not in st.session_state:
        st.session_state[k]=None

# ================= LOGIN =================
if not st.session_state.uid:
    st.markdown("## 💬 AOUSE CHAT")
    name = st.text_input("이름")
    theme = st.selectbox("테마", themes.keys())
    if st.button("시작"):
        uid=str(uuid.uuid4())
        users[uid]={"name":name,"theme":theme}
        save(USERS,users)
        st.session_state.uid=uid
        st.rerun()
    st.stop()

me = users[st.session_state.uid]
theme = themes[me["theme"]]

# ================= STYLE =================
st.markdown(f"""
<style>
body {{ background:{theme['bg']}; color:{theme['text']}; }}
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
}}
.me {{ background:{theme['me']}; color:white; margin-left:auto; }}
.other {{ background:{theme['card']}; }}
.small {{ font-size:11px; opacity:.6; }}
</style>
""", unsafe_allow_html=True)

# ================= THEME ADD =================
with st.sidebar:
    st.subheader("🎨 테마 추가")
    tname = st.text_input("테마 이름")
    bg = st.color_picker("배경")
    card = st.color_picker("카드")
    mec = st.color_picker("내 말풍선")
    btn = st.color_picker("버튼")
    txt = st.color_picker("텍스트")
    if st.button("➕ 추가"):
        themes[tname]={"bg":bg,"card":card,"me":mec,"btn":btn,"text":txt}
        save(THEMES_FILE,themes)
        st.success("테마 추가 완료")

    st.subheader("👤 프로필")
    me["name"] = st.text_input("이름", me["name"])
    me["theme"] = st.selectbox("테마 선택", themes.keys(), index=list(themes).index(me["theme"]))
    users[st.session_state.uid]=me
    save(USERS,users)

# ================= CHAT LIST =================
if not st.session_state.chat:
    st.markdown("## 💬 채팅")
    if st.button("➕ 1:1 채팅"):
        cid=str(uuid.uuid4())
        chats[cid]={"name":"1:1 채팅","members":[st.session_state.uid],"msgs":[],"pin":False,"group":False}
        save(CHATS,chats)

    if st.button("👥 그룹 채팅"):
        cid=str(uuid.uuid4())
        chats[cid]={"name":"그룹 채팅","members":[st.session_state.uid],"msgs":[],"pin":False,"group":True}
        save(CHATS,chats)

    def sort_key(item):
        last=item[1]["msgs"][-1]["time"] if item[1]["msgs"] else 0
        return (not item[1]["pin"], -last)

    for cid,c in sorted(chats.items(), key=sort_key):
        if st.session_state.uid in c["members"]:
            unread=sum(1 for m in c["msgs"] if st.session_state.uid not in m["read"])
            label=f"{'📌 ' if c['pin'] else ''}{'👥 ' if c['group'] else ''}{c['name']}"
            if unread: label+=f" 🔔 {unread}"
            if st.button(label, key=cid):
                st.session_state.chat=cid
                st.rerun()
    st.stop()

# ================= CHAT ROOM =================
cid=st.session_state.chat
chat=chats[cid]

st.markdown(f"### {chat['name']}")
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
        f"{'' if not m['img'] else f'<img src=\"{m['img']}\" width=\"100%\">'}"
        f"{'삭제된 메시지' if m['del'] else m['text']}"
        f"<br><span class='small'>❤️ {m['like']} {'✔✔' if len(m['read'])>1 else '✔'}</span>"
        f"</div>",
        unsafe_allow_html=True
    )

# ================= INPUT =================
text = st.text_area("메시지")
img = st.file_uploader("이미지", type=["png","jpg","jpeg"])

if st.button("전송"):
    img_path=""
    if img:
        name=f"{uuid.uuid4()}.png"
        path=f"{UPLOAD}/{name}"
        with open(path,"wb") as f: f.write(img.read())
        img_path=path

    chat["msgs"].append({
        "id":str(uuid.uuid4()),
        "user":st.session_state.uid,
        "text":text,
        "img":img_path,
        "time":time.time(),
        "read":[st.session_state.uid],
        "like":0,
        "del":False
    })
    save(CHATS,chats)
    st.rerun()
