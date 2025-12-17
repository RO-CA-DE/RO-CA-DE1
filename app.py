import streamlit as st
import json, os

# ================= BASIC =================
st.set_page_config(page_title="AOUSE", layout="centered")

DATA="data"
POSTS=f"{DATA}/posts.json"
USERS=f"{DATA}/users.json"
CHAPS=f"{DATA}/chapters.json"
AVATARS="avatars"
os.makedirs(DATA, exist_ok=True)
os.makedirs(AVATARS, exist_ok=True)

def load(p, d):
    if os.path.exists(p):
        with open(p,"r",encoding="utf-8") as f:
            return json.load(f)
    return d

def save(p, d):
    with open(p,"w",encoding="utf-8") as f:
        json.dump(d,f,ensure_ascii=False,indent=2)

users = load(USERS, {
    "ABLE":{"password":"1234","nickname":"ABLE_official","badge":"✔️","avatar":None}
})
posts = load(POSTS, [])
chapters = load(CHAPS, ["전체"])

s = st.session_state
for k,v in {
    "login":False,"user":None,"panel":None,
    "write":False,"open":None,"chapter":"전체"
}.items():
    s.setdefault(k,v)

# ================= HEADER =================
h1,h2,h3=st.columns([6,1,1])
with h1: st.markdown("## AOUSE")
with h2:
    if not s.login and st.button("ARRIVE"):
        s.panel="login"
with h3:
    if s.login and st.button("LOGOUT"):
        s.login=False; s.user=None; s.panel=None; st.rerun()

# ================= LOGIN =================
if s.panel=="login":
    uid=st.text_input("ID")
    pw=st.text_input("PW",type="password")
    if st.button("LOGIN"):
        if uid in users and users[uid]["password"]==pw:
            s.login=True; s.user=uid; s.panel=None; st.rerun()
        else: st.error("실패")

# ================= TOP =================
st.divider()
c1,c2,c3,c4,c5,c6=st.columns(6)
with c1: s.chapter=st.selectbox("게시물",chapters)
with c2:
    if s.login and st.button("게시물 쓰기"):
        s.write=not s.write; s.panel=None
with c3:
    if s.login and st.button("챕터 관리"):
        s.panel=None if s.panel=="chapter" else "chapter"; s.write=False
with c4:
    if s.login and st.button("계정 설정"):
        s.panel=None if s.panel=="profile" else "profile"; s.write=False
with c5:
    if s.login and st.button("로그인 설정"):
        s.panel=None if s.panel=="login_set" else "login_set"; s.write=False
with c6:
    if s.login and st.button("계정 추가"):
        s.panel=None if s.panel=="add" else "add"; s.write=False

# ================= CHAPTER =================
if s.panel=="chapter":
    st.subheader("📁 챕터 관리")
    new=st.text_input("새 챕터")
    if st.button("추가") and new and new not in chapters:
        chapters.append(new); save(CHAPS,chapters); st.rerun()
    for c in chapters[1:]:
        col1,col2=st.columns([4,1])
        col1.write(c)
        if col2.button("삭제",key=c):
            chapters.remove(c); save(CHAPS,chapters); st.rerun()

# ================= PROFILE =================
if s.panel=="profile":
    u=users[s.user]
    n=st.text_input("닉네임",u["nickname"])
    b=st.text_input("뱃지",u["badge"])
    if st.button("저장"):
        u["nickname"]=n; u["badge"]=b
        save(USERS,users); s.panel=None; st.rerun()

# ================= LOGIN SET =================
if s.panel=="login_set":
    nid=st.text_input("새 ID",s.user)
    npw=st.text_input("새 PW",type="password")
    if st.button("변경"):
        if nid!=s.user and nid in users:
            st.error("ID 중복")
        else:
            old=s.user
            if nid!=old:
                users[nid]=users.pop(old)
                for p in posts:
                    if p["author"]==old: p["author"]=nid
                    p["likes"]=[nid if x==old else x for x in p["likes"]]
                    for c in p["comments"]:
                        if c["author"]==old: c["author"]=nid
                s.user=nid
            if npw: users[s.user]["password"]=npw
            save(USERS,users); save(POSTS,posts)
            s.panel=None; st.rerun()

# ================= ADD ACCOUNT =================
if s.panel=="add":
    i=st.text_input("ID")
    p=st.text_input("PW",type="password")
    n=st.text_input("닉네임")
    if st.button("생성") and i and p and n:
        if i in users: st.error("중복")
        else:
            users[i]={"password":p,"nickname":n,"badge":"","avatar":None}
            save(USERS,users); st.success("완료")

# ================= WRITE =================
if s.write:
    t=st.text_input("제목")
    c=st.text_area("내용",height=200)
    ch=st.selectbox("챕터",chapters)
    pin=st.checkbox("📌 고정")
    if st.button("업로드"):
        posts.insert(0,{
            "title":t,"content":c,"chapter":ch,"author":s.user,
            "pinned":pin,"likes":[],"comments":[],"image":None
        })
        save(POSTS,posts); s.write=False; st.rerun()

# ================= POSTS =================
posts=sorted(posts,key=lambda x:(not x.get("pinned",False)))
for i,p in enumerate(posts):
    if s.chapter!="전체" and p["chapter"]!=s.chapter: continue
    if st.button(("📌 " if p["pinned"] else "")+p["title"],key=i):
        s.open=None if s.open==i else i
    if s.open==i:
        st.write(p["content"])
        if s.login and p["author"]==s.user:
            if st.button("삭제",key=f"d{i}"):
                posts.remove(p); save(POSTS,posts); s.open=None; st.rerun()
        st.write("❤️",len(p["likes"]))
        txt=st.text_input("댓글",key=f"c{i}")
        if st.button("등록",key=f"cb{i}") and txt:
            p["comments"].append({"author":s.user or "GUEST","text":txt})
            save(POSTS,posts); st.rerun()

