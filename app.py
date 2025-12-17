import streamlit as st
import json, os

# ================= STYLE =================
st.markdown("""
<style>
body { background-color:#f5f5f5; }
.post {
    background:white;
    padding:20px;
    border-radius:14px;
    margin-bottom:20px;
}
.title { font-size:20px; font-weight:700; }
.meta { color:#888; font-size:13px; margin-bottom:10px; }
button { border-radius:10px !important; }
</style>
""", unsafe_allow_html=True)

# ================= PATH =================
DATA = "data"
POSTS = f"{DATA}/posts.json"
USERS = f"{DATA}/users.json"
CHAPS = f"{DATA}/chapters.json"
AVATARS = "avatars"

os.makedirs(DATA, exist_ok=True)
os.makedirs(AVATARS, exist_ok=True)

# ================= UTILS =================
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
    "ABLE":{"password":"1234","nickname":"ABLE_official","badge":"✔️","avatar":None}
})
posts = load(POSTS,[])
chapters = load(CHAPS,["전체"])

# ================= SESSION =================
s = st.session_state
s.setdefault("login",False)
s.setdefault("user",None)
s.setdefault("login_popup",False)
s.setdefault("write_popup",False)
s.setdefault("edit_post",None)
s.setdefault("open_post",None)
s.setdefault("chapter","전체")
s.setdefault("profile",False)
s.setdefault("chapter_manage",False)

# ================= HEADER =================
h1,h2,h3 = st.columns([6,1,1])
with h1:
    st.markdown("## AOUSE")
with h2:
    if not s.login:
        if st.button("ARRIVE"):
            s.login_popup = True
with h3:
    if s.login:
        if st.button("LOGOUT"):
            s.login=False
            s.user=None
            st.rerun()

# ================= LOGIN =================
if s.login_popup:
    st.markdown("---")
    uid = st.text_input("ID")
    pw = st.text_input("Password",type="password")
    if st.button("LOGIN"):
        if uid in users and users[uid]["password"]==pw:
            s.login=True
            s.user=uid
            s.login_popup=False
            st.rerun()
        else:
            st.error("로그인 실패")

# ================= TOP BAR =================
st.divider()
c1,c2,c3,c4 = st.columns([3,2,2,2])

with c1:
    s.chapter = st.selectbox("게시물",chapters)

with c2:
    if s.login and st.button("게시물 쓰기"):
        s.write_popup=True

with c3:
    if s.login and st.button("챕터 관리"):
        s.chapter_manage=True

with c4:
    if s.login and st.button("계정 설정"):
        s.profile=True

# ================= CHAPTER MANAGE =================
if s.chapter_manage:
    st.markdown("---")
    st.subheader("챕터 관리")
    new = st.text_input("새 챕터")
    if st.button("추가") and new and new not in chapters:
        chapters.append(new)
        save(CHAPS,chapters)
        st.rerun()

    for ch in chapters[:]:
        if ch=="전체": continue
        col1,col2 = st.columns([4,1])
        with col1:
            rename = st.text_input("이름",ch,key=ch)
        with col2:
            if st.button("삭제",key=f"d{ch}"):
                chapters.remove(ch)
                for p in posts:
                    if p["chapter"]==ch: p["chapter"]="전체"
                save(CHAPS,chapters); save(POSTS,posts)
                st.rerun()
        if rename!=ch:
            i=chapters.index(ch)
            chapters[i]=rename
            for p in posts:
                if p["chapter"]==ch: p["chapter"]=rename
            save(CHAPS,chapters); save(POSTS,posts)
            st.rerun()

# ================= PROFILE =================
if s.profile:
    st.markdown("---")
    u = users[s.user]
    nick = st.text_input("닉네임",u["nickname"])
    badge = st.text_input("뱃지",u["badge"])
    avatar = st.file_uploader("프로필 사진",type=["png","jpg","jpeg"])
    if st.button("저장"):
        u["nickname"]=nick
        u["badge"]=badge
        if avatar:
            path=f"{AVATARS}/{s.user}.png"
            with open(path,"wb") as f: f.write(avatar.getbuffer())
            u["avatar"]=path
        save(USERS,users)
        s.profile=False
        st.rerun()

# ================= WRITE =================
if s.write_popup:
    st.markdown("---")
    t=st.text_input("제목")
    c=st.text_area("내용",height=200)
    ch=st.selectbox("챕터",chapters)
    img=st.file_uploader("이미지",type=["png","jpg","jpeg"])
    if st.button("업로드"):
        img_path=None
        if img:
            img_path=f"{DATA}/{img.name}"
            with open(img_path,"wb") as f: f.write(img.getbuffer())
        posts.insert(0,{
            "title":t,"content":c,"chapter":ch,
            "author":s.user,"image":img_path,
            "likes":[],"comments":[]
        })
        save(POSTS,posts)
        s.write_popup=False
        st.rerun()

# ================= POSTS =================
for i,p in enumerate(posts):
    if s.chapter!="전체" and p["chapter"]!=s.chapter: continue

    st.markdown("<div class='post'>",unsafe_allow_html=True)
    if st.button(p["title"],key=f"o{i}"):
        s.open_post = None if s.open_post==i else i

    u=users[p["author"]]
    st.markdown(f"<div class='meta'>[{p['chapter']}] {u['nickname']} {u['badge']}</div>",unsafe_allow_html=True)

    if s.open_post==i:
        st.write(p["content"])
        if p["image"] and os.path.exists(p["image"]):
            st.image(p["image"],use_container_width=True)

        # ❤️ LIKE
        if s.login:
            liked = s.user in p["likes"]
            if st.button(("❤️" if liked else "🤍")+f" {len(p['likes'])}",key=f"l{i}"):
                if liked: p["likes"].remove(s.user)
                else: p["likes"].append(s.user)
                save(POSTS,posts); st.rerun()
        else:
            st.caption(f"❤️ {len(p['likes'])}")

        # ✏️ EDIT
        if s.login and p["author"]==s.user:
            if st.button("✏️ 수정",key=f"e{i}"):
                s.edit_post=i; st.rerun()

        st.markdown("##### 댓글")
        for c in p["comments"]:
            st.caption(f"{c['author']}: {c['text']}")
        txt=st.text_input("댓글",key=f"c{i}")
        if st.button("등록",key=f"cb{i}") and txt:
            p["comments"].append({"author":s.user or "GUEST","text":txt})
            save(POSTS,posts); st.rerun()

    st.markdown("</div>",unsafe_allow_html=True)





