import streamlit as st
import os
from agent.react_agent import ReactAgent
from utils.chat_history_manager import ChatHistoryManager
import uuid

st.set_page_config(
    page_title="智能客服",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;600;700&display=swap');

* { font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif; }

#MainMenu, footer, header {visibility: hidden;}
.stDeployButton {display: none;}

.stApp { background: #F7F8FA; }

/* ── Top nav ── */
.top-nav {
    position: fixed; top: 0; left: 0; right: 0; height: 56px;
    background: #FFFFFF; border-bottom: 1px solid #E8E9ED;
    display: flex; align-items: center; padding: 0 24px;
    z-index: 999; box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.top-nav .nav-title {
    font-size: 18px; font-weight: 600; color: #1A1A2E;
    display: flex; align-items: center; gap: 10px;
}
.top-nav .nav-title .nav-icon {
    width: 32px; height: 32px;
    background: linear-gradient(135deg, #6C5CE7, #A29BFE);
    border-radius: 8px; display: flex; align-items: center;
    justify-content: center; color: white; font-size: 16px;
}
.top-nav .nav-status {
    margin-left: 16px; font-size: 12px; color: #00B894;
    background: #E6FFF5; padding: 2px 10px; border-radius: 12px; font-weight: 500;
}

/* ── Sidebar ── */
[data-testid="stSidebar"], section[data-testid="stSidebar"] {
    background: #1A1A2E !important; border-right: none !important;
}
[data-testid="stSidebar"] [data-testid="stMarkdown"],
section[data-testid="stSidebar"] [data-testid="stMarkdown"] {
    color: #E0E0E0;
}
[data-testid="stSidebar"] .stButton > button,
section[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #6C5CE7, #A29BFE) !important;
    color: white !important; border: none !important; border-radius: 10px !important;
    padding: 10px 0 !important; font-weight: 600 !important; font-size: 14px !important;
    width: 100% !important; transition: all 0.2s ease !important;
    box-shadow: 0 2px 8px rgba(108,92,231,0.3) !important;
}
[data-testid="stSidebar"] .stButton > button:hover,
section[data-testid="stSidebar"] .stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(108,92,231,0.4) !important;
}
[data-testid="stSidebar"] hr,
section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.08) !important;
}
[data-testid="stSidebar"] .stMarkdown h3,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #A0A0B8 !important; font-size: 12px !important; font-weight: 500 !important;
    text-transform: uppercase; letter-spacing: 1px;
}

/* Sidebar text & radio */
[data-testid="stSidebar"] .stRadio > div,
section[data-testid="stSidebar"] .stRadio > div { color: #E0E0E0; }
[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] label { color: #E0E0E0 !important; }

/* ── Admin panel in sidebar ── */
[data-testid="stSidebar"] .stExpander,
section[data-testid="stSidebar"] .stExpander {
    background: rgba(30,30,60,0.8) !important;
    border: 1px solid rgba(108,92,231,0.3) !important;
    border-radius: 10px !important;
    margin-bottom: 8px !important;
    overflow: hidden !important;
}
[data-testid="stSidebar"] .stExpander summary,
section[data-testid="stSidebar"] .stExpander summary {
    color: #E0E0E0 !important;
    font-weight: 600 !important;
    padding: 10px 14px !important;
}
[data-testid="stSidebar"] .stExpander summary:hover,
section[data-testid="stSidebar"] .stExpander summary:hover {
    background: rgba(108,92,231,0.1) !important;
}
[data-testid="stSidebar"] .stExpander [data-testid="stMarkdown"],
section[data-testid="stSidebar"] .stExpander [data-testid="stMarkdown"] {
    color: #C8C8D8 !important;
}
[data-testid="stSidebar"] .stExpander p,
section[data-testid="stSidebar"] .stExpander p {
    color: #C8C8D8 !important;
}

/* User list row styling */
.admin-user-row {
    display: flex; align-items: center; justify-content: space-between;
    background: rgba(255,255,255,0.04); border-radius: 8px;
    padding: 10px 12px; margin-bottom: 6px;
    border: 1px solid rgba(255,255,255,0.06);
}
.admin-user-row .username { color: #E0E0E0; font-size: 14px; font-weight: 500; flex: 1; }
.admin-user-row .role-badge {
    font-size: 11px; padding: 2px 10px; border-radius: 12px; font-weight: 500; margin-right: 8px;
}
.admin-user-row .role-badge.admin { background: #FF6B6B; color: white; }
.admin-user-row .role-badge.user { background: #4ECDC4; color: white; }

/* File list row */
.admin-file-row {
    display: flex; align-items: center; gap: 8px;
    background: rgba(255,255,255,0.04); border-radius: 6px;
    padding: 8px 12px; margin-bottom: 4px;
    color: #C8C8D8; font-size: 13px;
}
.admin-file-row .file-icon { font-size: 16px; }

/* Fix selectbox dropdown arrow white square */
[data-testid="stSidebar"] [data-testid="stSelectbox"] div[data-baseweb="select"],
section[data-testid="stSidebar"] [data-testid="stSelectbox"] div[data-baseweb="select"] {
    background-color: #2D2D4A !important;
}
[data-testid="stSidebar"] [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
section[data-testid="stSidebar"] [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    color: #E0E0E0 !important;
    background-color: #2D2D4A !important;
}
[data-testid="stSidebar"] [data-testid="stSelectbox"] svg,
section[data-testid="stSidebar"] [data-testid="stSelectbox"] svg {
    fill: #E0E0E0 !important;
}
[data-testid="stSidebar"] [data-testid="stSelectbox"] div[data-baseweb="popover"],
section[data-testid="stSidebar"] [data-testid="stSelectbox"] div[data-baseweb="popover"] {
    background-color: #2D2D4A !important;
}

/* Fix file uploader button */
[data-testid="stSidebar"] [data-testid="stFileUploader"] > section,
section[data-testid="stSidebar"] [data-testid="stFileUploader"] > section {
    background: rgba(108,92,231,0.1) !important;
    border: 2px dashed rgba(108,92,231,0.4) !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploader"] label,
section[data-testid="stSidebar"] [data-testid="stFileUploader"] label {
    color: #A29BFE !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploader"] button,
section[data-testid="stSidebar"] [data-testid="stFileUploader"] button {
    background: rgba(108,92,231,0.2) !important;
    color: #A29BFE !important;
    border: 1px solid rgba(108,92,231,0.4) !important;
}

/* ── Main ── */
[data-testid="stMain"] { padding-top: 56px !important; }

[data-testid="stChatMessage"] {
    border: none !important; border-radius: 16px !important;
    padding: 16px 20px !important; margin-bottom: 12px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important; animation: fadeInUp 0.3s ease;
}
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: linear-gradient(135deg, #6C5CE7, #A29BFE) !important;
    color: white !important; margin-left: 15% !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stMarkdown"],
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) p {
    color: white !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: #FFFFFF !important; border: 1px solid #ECECF0 !important; margin-right: 15% !important;
}

[data-testid="stChatInput"] {
    border-radius: 16px !important; border: 1px solid #E0E0E8 !important;
    background: #FFFFFF !important; box-shadow: 0 2px 12px rgba(0,0,0,0.06) !important; padding: 4px !important;
}
[data-testid="stChatInput"] textarea { font-size: 14px !important; color: #1A1A2E !important; }
[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, #6C5CE7, #A29BFE) !important;
    border-radius: 10px !important; border: none !important; color: white !important;
}

.welcome-container { text-align: center; padding: 80px 20px 40px; }
.welcome-icon {
    width: 72px; height: 72px; background: linear-gradient(135deg, #6C5CE7, #A29BFE);
    border-radius: 20px; display: inline-flex; align-items: center; justify-content: center;
    font-size: 36px; margin-bottom: 24px; box-shadow: 0 8px 24px rgba(108,92,231,0.25);
}
.welcome-title { font-size: 28px; font-weight: 700; color: #1A1A2E; margin-bottom: 8px; }
.welcome-subtitle { font-size: 15px; color: #8888A0; margin-bottom: 40px; }

div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
    background: #FFFFFF !important; border: 1px solid #ECECF0 !important; border-radius: 14px !important;
    padding: 18px 20px !important; text-align: left !important; transition: all 0.2s ease !important;
    height: auto !important; min-height: 90px !important; white-space: normal !important; box-shadow: none !important;
}
div[data-testid="stHorizontalBlock"] button[kind="secondary"]:hover {
    border-color: #6C5CE7 !important; box-shadow: 0 4px 16px rgba(108,92,231,0.12) !important;
}
.stSpinner > div { border-color: #6C5CE7 transparent transparent transparent !important; }

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #D0D0D8; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #B0B0B8; }

.user-badge {
    display: flex; align-items: center; gap: 10px; padding: 12px 0; color: #E0E0E0; font-size: 14px;
}
.user-badge .avatar {
    width: 32px; height: 32px; background: linear-gradient(135deg, #A29BFE, #6C5CE7);
    border-radius: 50%; display: flex; align-items: center; justify-content: center;
    color: white; font-size: 14px; font-weight: 600; flex-shrink: 0;
}
.user-badge .role-tag {
    font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: 500;
}
.role-tag.admin { background: #FF6B6B; color: white; }
.role-tag.user { background: #4ECDC4; color: white; }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.markdown("""
<div class="top-nav">
    <div class="nav-title">
        <div class="nav-icon">🤖</div>
        智能客服
    </div>
    <span class="nav-status">● 在线</span>
</div>
""", unsafe_allow_html=True)

# ── Session state init ──
if "manager" not in st.session_state:
    st.session_state["manager"] = ChatHistoryManager()

manager = st.session_state["manager"]

if "user" not in st.session_state:
    st.session_state["user"] = None

if "agent" not in st.session_state:
    st.session_state["agent"] = ReactAgent()

if "auth_page" not in st.session_state:
    st.session_state["auth_page"] = "login"

# ── Persistent login: restore from query_params on refresh ──
if st.session_state["user"] is None:
    params = st.query_params
    uid = params.get("uid", "")
    if uid:
        saved_user = manager.get_user(uid)
        if saved_user:
            st.session_state["user"] = saved_user
            if "session_id" not in st.session_state:
                st.session_state["session_id"] = str(uuid.uuid4())
            if "messages" not in st.session_state:
                st.session_state["messages"] = []
            if "conversations" not in st.session_state:
                st.session_state["conversations"] = {}
            st.query_params.clear()


def stream_capture(generator):
    full_response = ""
    for chunk in generator:
        full_response += chunk
        yield chunk
    st.session_state["_last_full_response"] = full_response


def go_register():
    st.session_state["auth_page"] = "register"

def go_login():
    st.session_state["auth_page"] = "login"


# ── Sidebar ──
with st.sidebar:
    st.markdown("### 控制面板")

    # ── Login ──
    if st.session_state["user"] is None:

        if st.session_state["auth_page"] == "login":
            st.markdown("##### 用户登录")
            login_user = st.text_input("用户名", key="login_user", placeholder="请输入用户名")
            login_pass = st.text_input("密码", key="login_pass", type="password", placeholder="请输入密码")

            if st.button("登 录", use_container_width=True, key="btn_login"):
                if login_user.strip() and login_pass:
                    user = manager.login_user(login_user.strip(), login_pass)
                    if user:
                        st.session_state["user"] = user
                        st.session_state["session_id"] = str(uuid.uuid4())
                        st.session_state["messages"] = []
                        st.session_state["conversations"] = {}
                        st.query_params["uid"] = user["id"]
                        st.rerun()
                    else:
                        st.error("用户名或密码错误")
                else:
                    st.warning("请输入用户名和密码")

            st.markdown("---")
            st.markdown(
                '<div style="text-align:center;color:#A0A0B8;font-size:13px;">'
                '还没有账号？'
                '<a href="#" onclick="parent.document.querySelector(\'[data-testid=stSidebar]\') '
                '.querySelectorAll(\'button\')[0].click()" style="color:#A29BFE;">去注册</a>'
                '</div>',
                unsafe_allow_html=True,
            )
            st.button("没有账号？点此注册", on_click=go_register, use_container_width=True, type="secondary")

        else:
            st.markdown("##### 用户注册")
            reg_user = st.text_input("用户名", key="reg_user", placeholder="设置登录用户名")
            reg_pass = st.text_input("密码", key="reg_pass", type="password", placeholder="设置登录密码（≥6位）")
            reg_pass2 = st.text_input("确认密码", key="reg_pass2", type="password", placeholder="再次输入密码")

            reg_role = st.radio(
                "注册身份", ["普通用户", "管理员"],
                horizontal=True, label_visibility="visible", key="reg_role"
            )

            admin_code = ""
            if reg_role == "管理员":
                admin_code = st.text_input(
                    "管理员验证码", key="admin_code", type="password",
                    placeholder="请输入管理员注册码"
                )

            if st.button("注 册", use_container_width=True, key="btn_register"):
                if not reg_user.strip():
                    st.error("请输入用户名")
                elif len(reg_pass) < 6:
                    st.error("密码长度至少 6 位")
                elif reg_pass != reg_pass2:
                    st.error("两次密码不一致")
                else:
                    role = "admin" if reg_role == "管理员" else "user"
                    if role == "admin" and admin_code != "admin888":
                        st.error("管理员验证码错误")
                    else:
                        try:
                            user = manager.register_user(reg_user.strip(), reg_pass, role)
                            st.session_state["user"] = user
                            st.session_state["session_id"] = str(uuid.uuid4())
                            st.session_state["messages"] = []
                            st.session_state["conversations"] = {}
                            st.query_params["uid"] = user["id"]
                            st.success("注册成功！")
                            st.rerun()
                        except ValueError as e:
                            st.error(str(e))

            st.markdown("---")
            st.button("已有账号？去登录", on_click=go_login, use_container_width=True, type="secondary")

    else:
        # ── Logged in ──
        user = st.session_state["user"]
        initial = user["username"][0].upper()
        role_label = "管理员" if user["role"] == "admin" else "普通用户"
        role_class = "admin" if user["role"] == "admin" else "user"
        st.markdown(
            f'<div class="user-badge">'
            f'<div class="avatar">{initial}</div>'
            f'<span>{user["username"]}</span>'
            f'<span class="role-tag {role_class}">{role_label}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if st.button("退出登录", use_container_width=True, type="secondary"):
            st.session_state["user"] = None
            st.session_state["session_id"] = str(uuid.uuid4())
            st.session_state["messages"] = []
            st.session_state["conversations"] = {}
            st.session_state["auth_page"] = "login"
            st.query_params.clear()
            st.rerun()

    st.markdown("---")

    # ── Session management (logged-in) ──
    if st.session_state["user"] is not None:
        user_id = st.session_state["user"]["id"]
        is_admin = st.session_state["user"]["role"] == "admin"

        if "session_id" not in st.session_state:
            st.session_state["session_id"] = str(uuid.uuid4())

        if "messages" not in st.session_state:
            st.session_state["messages"] = manager.get_history(st.session_state["session_id"])

        st.session_state["conversations"] = manager.get_user_sessions(user_id)

        def start_new_chat():
            if st.session_state["messages"]:
                title = st.session_state["messages"][0]["content"][:20] + "..."
                manager.update_session_title(st.session_state["session_id"], title)
            new_id = str(uuid.uuid4())
            manager.create_session(new_id, user_id)
            st.session_state["session_id"] = new_id
            st.session_state["messages"] = []

        st.button("＋ 新建对话", on_click=start_new_chat, use_container_width=True)
        st.markdown("---")

        if st.session_state["conversations"]:
            st.markdown("### 历史记录")
            for cid, conv in st.session_state["conversations"].items():
                is_active = cid == st.session_state["session_id"]
                label = f"{'● ' if is_active else '  '}💬 {conv['title']}"
                if st.button(label, key=f"session_{cid}", use_container_width=True,
                             type="secondary" if not is_active else "primary"):
                    if not is_active:
                        st.session_state["session_id"] = cid
                        st.session_state["messages"] = manager.get_history(cid)
                        st.rerun()

        # ── Admin panel ──
        if is_admin:
            st.markdown("---")
            st.markdown("### 管理后台")

            with st.expander("👥 用户管理", expanded=False):
                users = manager.list_users()
                if users:
                    for u in users:
                        role_class = u["role"]
                        role_label = "管理员" if u["role"] == "admin" else "普通用户"
                        st.markdown(
                            f'<div class="admin-user-row">'
                            f'<span class="username">{u["username"]}</span>'
                            f'<span class="role-badge {role_class}">{role_label}</span>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
                    st.markdown("---")

                    del_options = {
                        f"{u['username']} ({u['role']})": u["id"]
                        for u in users if u["id"] != user_id
                    }
                    if del_options:
                        selected = st.selectbox(
                            "选择要删除的用户",
                            list(del_options.keys()),
                            key="del_user_select",
                            label_visibility="visible",
                        )
                        if st.button("删除选中用户", use_container_width=True, type="primary", key="btn_del_user"):
                            uid = del_options[selected]
                            manager.delete_user(uid)
                            st.success(f"已删除用户 {selected}")
                            st.rerun()
                    else:
                        st.info("没有其他可删除的用户")
                else:
                    st.info("暂无注册用户")

            with st.expander("📚 知识库管理", expanded=False):
                data_dir = "data/"
                try:
                    files = sorted([
                        f for f in os.listdir(data_dir)
                        if f.endswith(('.pdf', '.txt', '.md'))
                    ])
                    if files:
                        for f in files:
                            ext = f.rsplit('.', 1)[-1].lower()
                            icon = {"pdf": "📕", "txt": "📄", "md": "📝"}.get(ext, "📄")
                            st.markdown(
                                f'<div class="admin-file-row">'
                                f'<span class="file-icon">{icon}</span>{f}'
                                f'</div>',
                                unsafe_allow_html=True,
                            )
                    else:
                        st.info("暂无知识库文件")
                except Exception:
                    st.info("暂无知识库文件")

                uploaded = st.file_uploader(
                    "上传知识库文件", type=["pdf", "txt", "md"],
                    key="upload_kb", accept_multiple_files=True,
                )
                if uploaded:
                    for file in uploaded:
                        save_path = os.path.join(data_dir, file.name)
                        with open(save_path, "wb") as f:
                            f.write(file.getbuffer())
                    st.success(f"已上传 {len(uploaded)} 个文件")
                    st.rerun()

    st.markdown("---")
    st.markdown(
        '<div style="text-align:center; color:#666680; font-size:11px; padding:12px 0;">'
        "Powered by ReAct Agent<br>© 2026 智能客服系统"
        "</div>",
        unsafe_allow_html=True,
    )


# ── Main chat area ──
if st.session_state["user"] is None:
    st.markdown(
        """
    <div class="welcome-container">
        <div class="welcome-icon">🤖</div>
        <div class="welcome-title">欢迎使用智能客服系统</div>
        <div class="welcome-subtitle">请先在左侧登录或注册账号，开始与 AI 助手对话</div>
    </div>
    """,
        unsafe_allow_html=True,
    )
else:
    prompt = None

    if not st.session_state["messages"]:
        st.markdown(
            """
        <div class="welcome-container">
            <div class="welcome-icon">🤖</div>
            <div class="welcome-title">你好，我是智能客服助手</div>
            <div class="welcome-subtitle">有任何问题都可以向我提问，我会尽力为您解答</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔧 故障排查\n扫地机器人无法开机怎么办？", use_container_width=True, key="q1"):
                prompt = "扫地机器人无法开机怎么办？"
            if st.button("🧹 清洁保养\n扫地机器人如何清洁保养？", use_container_width=True, key="q3"):
                prompt = "扫地机器人如何清洁保养？"
        with col2:
            if st.button("🛒 选购建议\n推荐一款性价比高的扫地机器人", use_container_width=True, key="q2"):
                prompt = "推荐一款性价比高的扫地机器人"
            if st.button("📋 常见问题\n扫地机器人常见故障有哪些？", use_container_width=True, key="q4"):
                prompt = "扫地机器人常见故障有哪些？"

    for message in st.session_state["messages"]:
        avatar = "🤖" if message["role"] == "assistant" else "👤"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    chat_input = st.chat_input("输入你的问题...")
    if chat_input:
        prompt = chat_input

    if prompt:
        user_id = st.session_state["user"]["id"]
        session_id = st.session_state["session_id"]

        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        st.session_state["messages"].append({"role": "user", "content": prompt})
        manager.add_message(session_id, user_id, "user", prompt)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("正在思考..."):
                res_stream = st.session_state["agent"].excute_stream(prompt)
                st.write_stream(stream_capture(res_stream))

        full_response = st.session_state.get("_last_full_response", "")
        if full_response:
            st.session_state["messages"].append({"role": "assistant", "content": full_response})
            manager.add_message(session_id, user_id, "assistant", full_response)
