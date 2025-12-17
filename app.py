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
.meta { color:#888; font-size:13px; margin-bottom:10px; }
button { border-radius:10px !important; }
</style>
""", unsafe_allow_html=True)

# ================= PATH =================
DATA="data"
POSTS=f"{DATA}/posts.json"
USERS=f"{DATA}/users.json"
CHAPS=f"{DATA}/chapters.json"
AVATARS="avatars"
os.makedirs(DATA,exist_ok=True)
os.makedirs(AVATARS,exist_ok=True)

# ================= UTILS =================
def load(p,d):
    if os.path.exists(p):
        with open(p,"r",encoding="utf-8") as f:
            return json.load(f)
    return d

def save(p,d):
    with open(p,"w",encoding="utf-8") as f:
        json.dump(d,f,ensure_ascii=False,indent=2)

# ================= DATA =================
users=load(USERS,{
    "ABLE":{"password":"1234","nickname":"ABLE_official","badge":"✔️","avatar":None}
})
posts=load(POSTS,[])
chapters=load(CHAPS,["전체"])

# ================= SESSION =================
s=st.session_state
s.setdefault("login",False)
s.setdefault("user",None)
s.setdefault("login_popup",False)
s.setdefault("write_popup",False)
s.setdefault("active_panel",None)
s.setdefault("open_post",None)
s.setdefault("chapter","전체")

# ================= HEADER =================
h1,h2,h3=st.columns([6,1,1])
with h1:
    st.markdown("## AOUSE")
with h2:
    if not s.login and st.button("ARRIVE"):
        s.login_popup=True
with h3:
    if s.login and st.button("LOGOUT"):
        s.login=False
        s.user=None
        s.active_panel=None
        st.rerun()

# ================= LOGIN =================
if s.login_popup:
    st.markdown("---")
    uid=st.text_input("ID")
    pw=st.text_input("Password",type="password")
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
c1,c2,c3,c4,c5,c6=st.columns([3,2,2,2,2,2])

with c1:
    s.chapter=st.selectbox("게시물",chapters)

with c2:
    if s.login and st.button("게시물 쓰기"):
        s.write_popup=not s.write_popup
        s.active_panel=None

with c3:
    if s.login and st.button("챕터 관리"):
        s.active_panel=None if s.active_panel=="chapter" else "chapter"
        s.write_popup=False

with c4:
    if s.login and st.button("계정 설정"):
        s.active_panel=None if s.active_panel=="profile" else "profile"
        s.write_popup=False

with c5:
    if s.login and st.button("로그인 설정"):
        s.active_panel=None if s.active_panel=="login_setting" else "login_setting"
        s.write_popup=False

with c6:
    if s.login and st.button("계정 추가"):
        s.active_panel=None if s.active_panel=="add_account" else "add_account"
        s.write_popup=False

# ================= WRITE =================
if s.write_popup:
    st.markdown("---")
    t=st.text_input("제목")
    c=st.text_area("내용",height=200)
    ch=st.selectbox("챕터",chapters)
    pin=st.checkbox("📌 게시물 고정")
    img=st.file_uploader("이미지",type=["png","jpg","jpeg"])
    if st.button("업로드"):
        img_path=None
        if img:
            img_path=f"{DATA}/{img.name}"
            with open(img_path,"wb") as f: f.write(img.getbuffer())
        posts.insert(0,{
            "title":t,"content":c,"chapter":ch,
            "author":s.user,"image":img_path,
            "pinned":pin,"likes":[],"comments":[]
        })
        save(POSTS,posts)
        s.write_popup=False
        st.rerun()

# ================= POSTS =================
sorted_posts=sorted(posts,key=lambda x:(not x.get("pinned",False),posts.index(x)))

for i,p in enumerate(sorted_posts):
    if s.chapter!="전체" and p["chapter"]!=s.chapter:
        continue

    st.markdown("<div class='post'>",unsafe_allow_html=True)

    title=("📌 " if p.get("pinned") else "") + p["title"]
    if st.button(title,key=f"o{i}"):
        s.open_post=None if s.open_post==i else i

    u=users[p["author"]]
    st.markdown(
        f"<div class='meta'>[{p['chapter']}] {u['nickname']} {u['badge']}</div>",
        unsafe_allow_html=True
    )

    if s.open_post==i:
        st.write(p["content"])
        if p["image"] and os.path.exists(p["image"]):
            st.image(p["image"],use_container_width=True)

        # ❤️ 좋아요
        if s.login:
            liked=s.user in p["likes"]
            if st.button(("❤️" if liked else "🤍")+f" {len(p['likes'])}",key=f"l{i}"):
                if liked:
                    p["likes"].remove(s.user)
                else:
                    p["likes"].append(s.user)
                save(POSTS,posts)
                st.rerun()
        else:
            st.caption(f"❤️ {len(p['likes'])}")

        # 🗑 본인 글 삭제
        if s.login and p["author"]==s.user:
            if st.button("🗑 게시물 삭제",key=f"d{i}"):
                posts.remove(p)
                save(POSTS,posts)
                s.open_post=None
                st.rerun()

        # 💬 댓글
        st.markdown("##### 댓글")
        for c in p["comments"]:
            st.caption(f"{c['author']}: {c['text']}")
        txt=st.text_input("댓글",key=f"c{i}")
        if st.button("등록",key=f"cb{i}") and txt:
            p["comments"].append({"author":s.user or "GUEST","text":txt})
            save(POSTS,posts)
            st.rerun()

    st.markdown("</div>",unsafe_allow_html=True)


