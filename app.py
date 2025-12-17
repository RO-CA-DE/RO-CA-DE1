import streamlit as st
import json, os

# ================== BASIC STYLE ==================
st.markdown("""
<style>
body {
    background-color: #f6f6f6;
}
.block-container {
    padding-top: 2rem;
}
.post-card {
    background: white;
    padding: 20px;
    border-radius: 14px;
    margin-bottom: 20px;
}
.post-title {
    font-size: 20px;
    font-weight: 700;
}
.post-meta {
    color: #888;
    font-size: 13px;
    margin-bottom: 10px;
}
.like-btn {
    border: none;
    background: none;
    font-size: 16px;
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

# ================== Paths ==================
DATA_DIR = "data"
POST_FILE = f"{DATA_DIR}/posts.json"
USER_FILE = f"{DATA_DIR}/users.json"
CHAPTER_FILE = f"{DATA_DIR}/chapters.json"

os.makedirs(DATA_DIR, exist_ok=True)

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
    "ABLE": {"password":"1234","nickname":"ABLE_official"},
    "BAEKAHJIN": {"password":"1234","nickname":"BAEKAHJIN"}
})

posts = load_json(POST_FILE, [])
chapters = load_json(CHAPTER_FILE, ["전체"])

# ================== Session ==================
defaults = {
    "logged_in": False,
    "current_user": None,
    "show_login": False,
    "show_write": False,
    "show_edit": None,
    "selected_chapter": "전체",
    "open_post": None
}
for k,v in defaults.items():
    st.session_state.setdefault(k, v)

# ================== Header ==================
h1,h2,h3 = st.columns([6,1,1])
with h1:
    st.markdown("## AOUSE")
with h2:
    if not st.session_state.logged_in:
        if st.button("ARRIVE"):
            st.session_state.show_login = True
with h3:
    if st.session_state.logged_in:
        if st.button("LOGOUT"):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.rerun()

# ================== Login ==================
if st.session_state.show_login:
    st.markdown("---")
    uid = st.text_input("ID")
    pw = st.text_input("Password", type="password")
    if st.button("LOGIN"):
        if uid in users and users[uid]["password"] == pw:
            st.session_state.logged_in = True
            st.session_state.current_user = uid
            st.session_state.show_login = False
            st.rerun()
        else:
            st.error("로그인 실패")

# ================== Top Bar ==================
st.divider()
c1,c2 = st.columns([3,2])
with c1:
    st.session_state.selected_chapter = st.selectbox("게시물", chapters)
with c2:
    if st.session_state.logged_in:
        if st.button("게시물 쓰기"):
            st.session_state.show_write = True

# ================== Write ==================
if st.session_state.show_write:
    st.markdown("---")
    title = st.text_input("제목")
    content = st.text_area("내용", height=200)
    chapter = st.selectbox("챕터", chapters)

    if st.button("업로드"):
        posts.insert(0,{
            "title": title,
            "content": content,
            "chapter": chapter,
            "author": st.session_state.current_user,
            "likes": [],
            "comments": []
        })
        save_json(POST_FILE, posts)
        st.session_state.show_write = False
        st.rerun()

# ================== Edit ==================
if st.session_state.show_edit is not None:
    p = posts[st.session_state.show_edit]
    st.markdown("---")
    st.subheader("게시물 수정")
    title = st.text_input("제목", p["title"])
    content = st.text_area("내용", p["content"], height=200)
    chapter = st.selectbox("챕터", chapters, index=chapters.index(p.get("chapter","전체")))

    if st.button("저장"):
        p["title"] = title
        p["content"] = content
        p["chapter"] = chapter
        save_json(POST_FILE, posts)
        st.session_state.show_edit = None
        st.rerun()

# ================== Posts ==================
for idx, p in enumerate(posts):

    if st.session_state.selected_chapter != "전체" and p.get("chapter","전체") != st.session_state.selected_chapter:
        continue

    st.markdown("<div class='post-card'>", unsafe_allow_html=True)

    if st.button(p["title"], key=f"o{idx}"):
        st.session_state.open_post = idx if st.session_state.open_post != idx else None

    st.markdown(
        f"<div class='post-meta'>[{p.get('chapter','전체')}] {users[p['author']]['nickname']}</div>",
        unsafe_allow_html=True
    )

    if st.session_state.open_post == idx:
        st.write(p["content"])

        # ❤️ Like
        user = st.session_state.current_user
        likes = p.setdefault("likes", [])
        liked = user in likes if user else False

        if st.session_state.logged_in:
            if st.button(f"{'❤️' if liked else '🤍'} {len(likes)}", key=f"l{idx}"):
                if liked:
                    likes.remove(user)
                else:
                    likes.append(user)
                save_json(POST_FILE, posts)
                st.rerun()
        else:
            st.caption(f"❤️ {len(likes)}")

        # ✏️ Edit
        if st.session_state.logged_in and p["author"] == user:
            if st.button("✏️ 수정", key=f"e{idx}"):
                st.session_state.show_edit = idx
                st.rerun()

        st.markdown("#### 댓글")
        for c in p.get("comments", []):
            st.caption(f"{c['author']}: {c['text']}")

        txt = st.text_input("댓글 작성", key=f"c{idx}")
        if st.button("등록", key=f"cb{idx}") and txt:
            p.setdefault("comments", []).append({
                "author": user or "GUEST",
                "text": txt
            })
            save_json(POST_FILE, posts)
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)






