import streamlit as st
import json, os, uuid

# ================= BASIC =================
st.set_page_config(page_title="AOUSE", layout="centered")

DATA="data"
POSTS=f"{DATA}/posts.json"
USERS=f"{DATA}/users.json"
CHAPS=f"{DATA}/chapters.json"
os.makedirs(DATA, exist_ok=True)

def load(p, d):
    if os.path.exists(p):
        with open(p,"r",encoding="utf-8") as f:
            return json.load(f)
    return d

def save(p, d):
    with open(p,"w",encoding="utf-8") as f:
        json.dump(d,f,ensure_ascii=False,indent=2)

# ================= DATA =================
users = load(USERS,{
    "ABLE":{"password":"1234","nickname":"ABLE_official","badge":"✔️"}
})
posts = load(POSTS,[])
chapters = load(CHAPS,["전체"])

# ================= SESSION =================
s=st.session_state
for k,v in {
    "login":False,"user":None,"panel":None,
    "write":False,"edit":None,"open":None,"chapter":"전체"
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
        else: st.error("로그인 실패")

# ================= TOP =================
st.divider()
c1,c2,c3=st.columns(3)
with c1: s.chapter=st.selectbox("게시물",chapters)
with c2:
    if s.login and st.button("게시물 쓰기"):
        s.write=not s.write; s.edit=None
with c3:
    if s.login and st.button("계정 설정"):
        s.panel=None if s.panel=="profile" else "profile"; s.write=False

# ================= WRITE =================
if s.write:
    st.subheader("게시물 작성")
    t=st.text_input("제목")
    c=st.text_area("내용",height=200)
    ch=st.selectbox("챕터",chapters)
    pin=st.checkbox("📌 고정")
    img=st.file_uploader("사진 업로드",type=["png","jpg","jpeg"])

    if st.button("업로드"):
        img_path=None
        if img:
            img_path=f"{DATA}/{uuid.uuid4()}_{img.name}"
            with open(img_path,"wb") as f: f.write(img.getbuffer())

        posts.insert(0,{
            "id":str(uuid.uuid4()),
            "title":t,"content":c,"chapter":ch,
            "author":s.user,"pinned":pin,
            "image":img_path,"likes":[],"comments":[]
        })
        save(POSTS,posts)
        s.write=False
        st.rerun()

# ================= POSTS =================
posts=sorted(posts,key=lambda x:(not x["pinned"]))
for i,p in enumerate(posts):
    if s.chapter!="전체" and p["chapter"]!=s.chapter: continue

    if st.button(("📌 " if p["pinned"] else "")+p["title"],key=p["id"]):
        s.open=None if s.open==p["id"] else p["id"]
        s.edit=None

    if s.open==p["id"]:
        st.markdown(f"**작성자:** {p['author']}")
        st.write(p["content"])

        if p["image"] and os.path.exists(p["image"]):
            st.image(p["image"],use_container_width=True)

        # ===== 수정 버튼 =====
        if s.login and p["author"]==s.user and st.button("✏️ 수정"):
            s.edit=p["id"]

        # ===== 삭제 버튼 =====
        if s.login and p["author"]==s.user and st.button("🗑 삭제"):
            posts.remove(p); save(POSTS,posts); s.open=None; st.rerun()

        # ===== 수정 모드 =====
        if s.edit==p["id"]:
            st.markdown("### 게시물 수정")
            nt=st.text_input("제목",p["title"])
            nc=st.text_area("내용",p["content"],height=200)
            nch=st.selectbox("챕터",chapters,index=chapters.index(p["chapter"]))
            npin=st.checkbox("📌 고정",p["pinned"])
            nimg=st.file_uploader("사진 변경",type=["png","jpg","jpeg"])

            if st.button("저장"):
                p["title"]=nt
                p["content"]=nc
                p["chapter"]=nch
                p["pinned"]=npin

                if nimg:
                    path=f"{DATA}/{uuid.uuid4()}_{nimg.name}"
                    with open(path,"wb") as f: f.write(nimg.getbuffer())
                    p["image"]=path

                save(POSTS,posts)
                s.edit=None
                st.rerun()

        # ===== 댓글 =====
        st.markdown("##### 댓글")
        for c in p["comments"]:
            st.caption(f"{c['author']}: {c['text']}")
        txt=st.text_input("댓글",key=f"c{i}")
        if st.button("등록",key=f"cb{i}") and txt:
            p["comments"].append({"author":s.user or "GUEST","text":txt})
            save(POSTS,posts); st.rerun()


