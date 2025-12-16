import streamlit as st
from PIL import Image
import json
import os

# ================== File Paths ==================
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

# ================== Data Load ==================
users = load_json(USER_FILE, {
    "ABLE": {
        "password": "1234",
        "nickname": "ABLE_official",
        "badge": "✔️",
        "avatar": None,
        "is_admin": True
    },
    "BAEKAHJIN": {
        "password": "1234",
        "nickname": "BAEKAHJIN_official",
        "badge": "✔️",
        "avatar": None,
        "is_admin": False
    },
    "ARCEN": {
        "password": "1234",
        "nickname": "ARCEN",
        "badge": "✔️",
        "avatar": None,
        "is_admin": False
    }
})

posts = load_json(POST_FILE, [])

# ================== Session ==================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# ================== Header ==================
col1, col2, col3 = st.columns([5, 1, 1])
with col1:
    st.markdown("## AOUSE")
with col2:
    if not st.session_state.logged_in:
        if st.button("ARRIVE"):
            st.session_state.show_login = True
with col3:
    if st.session_state.logged_in:
        if st.button("LOGOUT"):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.rerun()

# ================== Login Modal ==================
if st.session_state.get("show_login"):
    with st.modal("ARRIVE"):
        uid = st.text_input("ID")
        pw = st.text_input("Password", type="password")
        if st.button("ARRIVE"):
            user = users.get(uid)
            if user and user["password"] == pw:
                st.session_state.logged_in = True
                st.session_state.current_user = uid
                st.session_state.show_login = False
                st.rerun()
            else:
                st.error("로그인 실패")

# ================== Top Bar ==================
st.divider()
if st.session_state.logged_in:
    col1, col2, col3 = st.columns([3, 2, 2])
    with col1:
        st.selectbox("게시글", ["게시글"])
    with col2:
        if st.button("게시물 쓰기"):
            st.session_state.show_write = True
    with col3:
        if st.button("계정 설정"):
            st.session_state.show_profile = True
else:
    col1, col2 = st.columns([3, 2])
    with col1:
        st.selectbox("게시글", ["게시글"])
    with col2:
        st.selectbox("전체", ["전체"])

# ================== Profile Modal ==================
if st.session_state.get("show_profile"):
    with st.modal("계정 설정"):
        u = users[st.session_state.current_user]
        nickname = st.text_input("닉네임", u["nickname"])
        badge = st.text_input("뱃지", u["badge"])
        avatar = st.file_uploader("프로필 사진", type=["png","jpg","jpeg"])
        if st.button("저장"):
            u["nickname"] = nickname
            u["badge"] = badge
            if avatar:
                path = f"{AVATAR_DIR}/{st.session_state.current_user}.png"
                with open(path, "wb") as f:
                    f.write(avatar.getbuffer())
                u["avatar"] = path
            save_json(USER_FILE, users)
            st.session_state.show_profile = False
            st.rerun()

# ================== Write Post Modal ==================
if st.session_state.get("show_write"):
    with st.modal("게시물 작성"):
        title = st.text_input("제목")
        content = st.text_area("내용")
        image = st.file_uploader("사진 업로드", type=["png","jpg","jpeg"])
        pinned = False
        if users[st.session_state.current_user]["is_admin"]:
            pinned = st.checkbox("📌 핀 고정 게시물")

        if st.button("게시물 업로드"):
            post_img = None
            if image:
                img_path = f"{DATA_DIR}/{image.name}"
                with open(img_path, "wb") as f:
                    f.write(image.getbuffer())
                post_img = img_path

            posts.insert(0, {
                "title": title,
                "content": content,
                "author": st.session_state.current_user,
                "image": post_img,
                "pinned": pinned
            })
            save_json(POST_FILE, posts)
            st.session_state.show_write = False
            st.rerun()

# ================== Edit Post Modal ==================
if st.session_state.get("edit_index") is not None:
    idx = st.session_state.edit_index
    post = posts[idx]
    with st.modal("게시물 수정"):
        title = st.text_input("제목", post["title"])
        content = st.text_area("내용", post["content"])
        if st.button("수정 완료"):
            post["title"] = title
            post["content"] = content
            save_json(POST_FILE, posts)
            st.session_state.edit_index = None
            st.rerun()

# ================== Post List ==================
sorted_posts = sorted(
    enumerate(posts),
    key=lambda x: x[1].get("pinned", False),
    reverse=True
)

for idx, p in sorted_posts:
    st.markdown("---")
    u = users[p["author"]]
    cols = st.columns([1, 7, 2])
    with cols[0]:
        if u.get("avatar") and os.path.exists(u["avatar"]):
            st.image(u["avatar"], width=50)
        else:
            st.image("https://via.placeholder.com/50", width=50)
    with cols[1]:
        pin = "📌 " if p.get("pinned") else ""
        st.markdown(f"{pin}**{p['title']}**")
        st.caption(f"{u['nickname']} {u['badge']}")
        st.write(p["content"])
        if p.get("image") and os.path.exists(p["image"]):
            st.image(p["image"], use_container_width=True)
    with cols[2]:
        if st.session_state.logged_in and p["author"] == st.session_state.current_user:
            if st.button("수정", key=f"edit{idx}"):
                st.session_state.edit_index = idx
            if st.button("삭제", key=f"del{idx}"):
                posts.pop(idx)
                save_json(POST_FILE, posts)
                st.rerun()
