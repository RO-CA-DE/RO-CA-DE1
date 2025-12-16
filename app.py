import streamlit as st
import json, os

# ================== Paths ==================
DATA_DIR = "data"
POST_FILE = f"{DATA_DIR}/posts.json"
USER_FILE = f"{DATA_DIR}/users.json"
CHAPTER_FILE = f"{DATA_DIR}/chapters.json"
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
    "BAEKAHJIN": {"password":"1234","nickname":"BAEKAHJIN","badge":"","avatar":None,"is_admin":False}
})

posts = load_json(POST_FILE, [])
chapters = load_json(CHAPTER_FILE, ["전체"])

# ================== Session ==================
defaults = {
    "logged_in": False,
    "current_user": None,
    "show_login": False,
    "show_write": False,
    "show_profile": False,
    "show_chapter": False,
    "selected_chapter": "전체",
    "open_post": None
}
for k,v in defaults.items():
    st.session_state.setdefault(k, v)

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

# ================== Login ==================
if st.session_state.show_login:
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
a,b,c,d = st.columns([3,2,2,2])

with a:
    selected = st.selectbox("게시물", chapters, index=chapters.index(st.session_state.selected_chapter))
    st.session_state.selected_chapter = selected

with b:
    if st.session_state.logged_in:
        if st.button("게시물 쓰기"):
            st.session_state.show_write = True

with c:
    if st.session_state.logged_in:
        if st.button("챕터 관리"):
            st.session_state.show_chapter = True

with d:
    if st.session_state.logged_in:
        if st.button("계정 설정"):
            st.session_state.show_profile = True

# ================== Chapter Admin ==================
if st.session_state.show_chapter:
    st.markdown("---")
    st.subheader("챕터 관리")

    if users[st.session_state.current_user]["is_admin"]:
        new_ch = st.text_input("새 챕터")
        if st.button("추가") and new_ch:
            if new_ch not in chapters:
                chapters.append(new_ch)
                save_json(CHAPTER_FILE, chapters)
                st.rerun()

        for ch in list(chapters):
            if ch == "전체": continue

            c1,c2 = st.columns([4,1])
            with c1:
                rename = st.text_input(f"이름 수정 - {ch}", ch, key=f"r{ch}")
            with c2:
                if st.button("삭제", key=f"d{ch}"):
                    chapters.remove(ch)
                    for p in posts:
                        if p.get("chapter") == ch:
                            p["chapter"] = "전체"
                    save_json(CHAPTER_FILE, chapters)
                    save_json(POST_FILE, posts)
                    st.rerun()

            if rename != ch:
                i = chapters.index(ch)
                chapters[i] = rename
                for p in posts:
                    if p.get("chapter") == ch:
                        p["chapter"] = rename
                save_json(CHAPTER_FILE, chapters)
                save_json(POST_FILE, posts)
                st.rerun()
    else:
        st.caption("관리자만 수정 가능")

# ================== Profile ==================
if st.session_state.show_profile:
    st.markdown("---")
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

# ================== Write ==================
if st.session_state.show_write:
    st.markdown("---")
    st.subheader("게시물 작성")

    title = st.text_input("제목")
    content = st.text_area("내용", height=200)
    chapter = st.selectbox("챕터", chapters)
    image = st.file_uploader("사진 업로드", type=["png","jpg","jpeg"])

    if st.button("업로드"):
        img_path = None
        if image:
            img_path = f"{DATA_DIR}/{image.name}"
            with open(img_path,"wb") as f:
                f.write(image.getbuffer())

        posts.insert(0,{
            "title": title,
            "content": content,
            "author": st.session_state.current_user,
            "chapter": chapter,
            "image": img_path,
            "comments": [],
            "admin_replies": []
        })
        save_json(POST_FILE, posts)
        st.session_state.show_write = False
        st.rerun()

# ================== Posts ==================
for idx, p in enumerate(posts):

    if st.session_state.selected_chapter != "전체" and p.get("chapter","전체") != st.session_state.selected_chapter:
        continue

    st.markdown("---")
    if st.button(p["title"], key=f"open{idx}"):
        st.session_state.open_post = idx if st.session_state.open_post != idx else None

    author = users.get(p["author"], {"nickname":"GUEST","badge":""})
    st.caption(f"[{p.get('chapter','전체')}] {author['nickname']} {author['badge']}")

    if st.session_state.open_post == idx:
        st.write(p["content"])

        if p.get("image") and os.path.exists(p["image"]):
            st.image(p["image"], use_container_width=True)

        st.markdown("#### 댓글")
        for ci, c in enumerate(p.get("comments", [])):
            st.caption(f"{c.get('author','GUEST')}: {c.get('text','')}")

        txt = st.text_input("댓글 작성", key=f"c{idx}")
        if st.button("등록", key=f"cb{idx}") and txt:
            p.setdefault("comments", []).append({
                "author": st.session_state.current_user or "GUEST",
                "text": txt
            })
            save_json(POST_FILE, posts)
            st.rerun()






