import streamlit as st
import json
import os

# ================== Paths ==================
DATA_DIR = "data"
POST_FILE = f"{DATA_DIR}/posts.json"
USER_FILE = f"{DATA_DIR}/users.json"
AVATAR_DIR = "avatars"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(AVATAR_DIR, exist_ok=True)

# ================== Utils ==================
def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ================== Data ==================
users = load_json(USER_FILE, {
    "ABLE": {"password":"1234","nickname":"ABLE_official","badge":"✔️","avatar":None,"is_admin":True},
    "BAEKAHJIN": {"password":"1234","nickname":"BAEKAHJIN_official","badge":"✔️","avatar":None,"is_admin":False},
    "ARCEN": {"password":"1234","nickname":"ARCEN","badge":"✔️","avatar":None,"is_admin":False}
})

posts = load_json(POST_FILE, [])

# ================== Session ==================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "show_login" not in st.session_state:
    st.session_state.show_login = False
if "show_write" not in st.session_state:
    st.session_state.show_write = False
if "show_profile" not in st.session_state:
    st.session_state.show_profile = False
if "edit_idx" not in st.session_state:
    st.session_state.edit_idx = None

# ================== Header ==================
c1,c2,c3 = st.columns([6,1,1])
with c1:
    st.markdown("## AOUSE")
with c2:
    if not st.session_state.logged_in:
        if st.button("ARRIVE"):
            st.session_state.show_login = True
with c3:
    if st.session_state.logged_in:
        if st.button("LOGOUT"):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.rerun()

# ================== LOGIN (NO MODAL) ==================
if st.session_state.show_login and not st.session_state.logged_in:
    st.markdown("---")
    st.subheader("ARRIVE")
    uid = st.text_input("ID")
    pw = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        u = users.get(uid)
        if u and u["password"] == pw:
            st.session_state.logged_in = True
            st.session_state.current_user = uid
            st.session_state.show_login = False
            st.rerun()
        else:
            st.error("로그인 실패")

# ================== Top Bar ==================
st.divider()
if st.session_state.logged_in:
    a,b,c = st.columns([3,2,2])
    with a:
        st.selectbox("게시글", ["게시글"])
    with b:
        if st.button("게시물 쓰기"):
            st.session_state.show_write = True
    with c:
        if st.button("계정 설정"):
            st.session_state.show_profile = True
else:
    a,b = st.columns([3,2])
    with a:
        st.selectbox("게시글", ["게시글"])
    with b:
        st.selectbox("전체", ["전체"])

# ================== PROFILE ==================
if st.session_state.show_profile:
    st.markdown("---")
    st.subheader("계정 설정")
    u = users[st.session_state.current_user]
    nickname = st.text_input("닉네임", u["nickname"])
    badge = st.text_input("뱃지", u["badge"])
    avatar = st.file_uploader("프로필 사진", type=["png","jpg","jpeg"])
    if st.button("저장"):
        u["nickname"] = nickname
        u["badge"] = badge
        if avatar:
            path = f"{AVATAR_DIR}/{st.session_state.current_user}.png"
            with open(path,"wb") as f:
                f.write(avatar.getbuffer())
            u["avatar"] = path
        save_json(USER_FILE, users)
        st.session_state.show_profile = False
        st.rerun()

# ================== WRITE ==================
if st.session_state.show_write:
    st.markdown("---")
    st.subheader("게시물 작성")
    title = st.text_input("제목")
    content = st.text_area("내용")
    image = st.file_uploader("사진 업로드", type=["png","jpg","jpeg"])
    pinned = False
    if users[st.session_state.current_user]["is_admin"]:
        pinned = st.checkbox("📌 핀 고정 게시물")

    if st.button("게시물 업로드"):
        img_path = None
        if image:
            img_path = f"{DATA_DIR}/{image.name}"
            with open(img_path,"wb") as f:
                f.write(image.getbuffer())

        posts.insert(0,{
            "title":title,
            "content":content,
            "author":st.session_state.current_user,
            "image":img_path,
            "pinned":pinned
        })
        save_json(POST_FILE, posts)
        st.session_state.show_write = False
        st.rerun()

# ================== POSTS ==================
sorted_posts = sorted(
    enumerate(posts),
    key=lambda x: x[1].get("pinned",False),
    reverse=True
)

for idx,p in sorted_posts:
    st.markdown("---")
    u = users[p["author"]]
    l,m,r = st.columns([1,7,2])
    with l:
        if u.get("avatar") and os.path.exists(u["avatar"]):
            st.image(u["avatar"], width=48)
        else:
            st.image("https://via.placeholder.com/48", width=48)
    with m:
        pin = "📌 " if p.get("pinned") else ""
        st.markdown(f"{pin}**{p['title']}**")
        st.caption(f"{u['nickname']} {u['badge']}")
        st.write(p["content"])
        if p.get("image") and os.path.exists(p["image"]):
            st.image(p["image"], use_container_width=True)
    with r:
        if st.session_state.logged_in and p["author"] == st.session_state.current_user:
            if st.button("수정", key=f"e{idx}"):
                st.session_state.edit_idx = idx
            if st.button("삭제", key=f"d{idx}"):
                posts.pop(idx)
                save_json(POST_FILE, posts)
                st.rerun()
