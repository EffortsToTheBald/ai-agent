import streamlit as st
from agent.react_agent import ReactAgent
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

* {
    font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* ── Hide default Streamlit elements ── */
#MainMenu, footer, header {visibility: hidden;}
.stDeployButton {display: none;}

/* ── Page background ── */
.stApp {
    background: #F7F8FA;
}

/* ── Top navigation bar ── */
.top-nav {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 56px;
    background: #FFFFFF;
    border-bottom: 1px solid #E8E9ED;
    display: flex;
    align-items: center;
    padding: 0 24px;
    z-index: 999;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

.top-nav .nav-title {
    font-size: 18px;
    font-weight: 600;
    color: #1A1A2E;
    display: flex;
    align-items: center;
    gap: 10px;
}

.top-nav .nav-title .nav-icon {
    width: 32px;
    height: 32px;
    background: linear-gradient(135deg, #6C5CE7, #A29BFE);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 16px;
}

.top-nav .nav-status {
    margin-left: 16px;
    font-size: 12px;
    color: #00B894;
    background: #E6FFF5;
    padding: 2px 10px;
    border-radius: 12px;
    font-weight: 500;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #1A1A2E !important;
    border-right: none !important;
    padding-top: 0 !important;
}

[data-testid="stSidebar"] [data-testid="stMarkdown"] {
    color: #E0E0E0;
}

[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #6C5CE7, #A29BFE) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 0 !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 8px rgba(108,92,231,0.3) !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(108,92,231,0.4) !important;
}

[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.08) !important;
}

[data-testid="stSidebar"] .stMarkdown h3 {
    color: #A0A0B8 !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.sidebar-chat-item {
    padding: 10px 14px;
    border-radius: 8px;
    margin-bottom: 4px;
    cursor: pointer;
    color: #C8C8D8;
    font-size: 13px;
    transition: all 0.15s ease;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.sidebar-chat-item:hover {
    background: rgba(255,255,255,0.06);
    color: #FFFFFF;
}

.sidebar-chat-item.active {
    background: rgba(108,92,231,0.2);
    color: #A29BFE;
}

/* ── Main content area offset for top nav ── */
[data-testid="stMain"] {
    padding-top: 56px !important;
}

/* ── Chat area ── */
[data-testid="stChatMessage"] {
    border: none !important;
    border-radius: 16px !important;
    padding: 16px 20px !important;
    margin-bottom: 12px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
    animation: fadeInUp 0.3s ease;
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}

/* User message - right aligned, purple */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: linear-gradient(135deg, #6C5CE7, #A29BFE) !important;
    color: white !important;
    margin-left: 15% !important;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stMarkdown"] {
    color: white !important;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) p {
    color: white !important;
}

/* Assistant message - left aligned, white */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: #FFFFFF !important;
    border: 1px solid #ECECF0 !important;
    margin-right: 15% !important;
}

/* ── Chat input ── */
[data-testid="stChatInput"] {
    border-radius: 16px !important;
    border: 1px solid #E0E0E8 !important;
    background: #FFFFFF !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06) !important;
    padding: 4px !important;
}

[data-testid="stChatInput"] textarea {
    font-size: 14px !important;
    color: #1A1A2E !important;
}

[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, #6C5CE7, #A29BFE) !important;
    border-radius: 10px !important;
    border: none !important;
    color: white !important;
}

/* ── Welcome screen ── */
.welcome-container {
    text-align: center;
    padding: 80px 20px 40px;
}

.welcome-icon {
    width: 72px;
    height: 72px;
    background: linear-gradient(135deg, #6C5CE7, #A29BFE);
    border-radius: 20px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 36px;
    margin-bottom: 24px;
    box-shadow: 0 8px 24px rgba(108,92,231,0.25);
}

.welcome-title {
    font-size: 28px;
    font-weight: 700;
    color: #1A1A2E;
    margin-bottom: 8px;
}

.welcome-subtitle {
    font-size: 15px;
    color: #8888A0;
    margin-bottom: 40px;
}

/* ── Quick action buttons ── */
div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
    background: #FFFFFF !important;
    border: 1px solid #ECECF0 !important;
    border-radius: 14px !important;
    padding: 18px 20px !important;
    text-align: left !important;
    transition: all 0.2s ease !important;
    height: auto !important;
    min-height: 90px !important;
    white-space: normal !important;
    box-shadow: none !important;
}

div[data-testid="stHorizontalBlock"] button[kind="secondary"]:hover {
    border-color: #6C5CE7 !important;
    box-shadow: 0 4px 16px rgba(108,92,231,0.12) !important;
}

/* ── Spinner styling ── */
.stSpinner > div {
    border-color: #6C5CE7 transparent transparent transparent !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar {
    width: 6px;
}
::-webkit-scrollbar-track {
    background: transparent;
}
::-webkit-scrollbar-thumb {
    background: #D0D0D8;
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
    background: #B0B0B8;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ── Top navigation bar ──
st.markdown("""
<div class="top-nav">
    <div class="nav-title">
        <div class="nav-icon">🤖</div>
        智能客服
    </div>
    <span class="nav-status">● 在线</span>
</div>
""", unsafe_allow_html=True)

# ── Session state initialization ──
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())

if "agent" not in st.session_state:
    st.session_state["agent"] = ReactAgent()

if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "conversations" not in st.session_state:
    st.session_state["conversations"] = {}


def stream_capture(generator):
    full_response = ""
    for chunk in generator:
        full_response += chunk
        yield chunk
    st.session_state["_last_full_response"] = full_response


def start_new_chat():
    if st.session_state["messages"]:
        title = st.session_state["messages"][0]["content"][:20] + "..."
        st.session_state["conversations"][st.session_state["session_id"]] = {
            "title": title,
            "messages": st.session_state["messages"],
        }
    st.session_state["session_id"] = str(uuid.uuid4())
    st.session_state["messages"] = []


# ── Sidebar ──
with st.sidebar:
    st.markdown("### 控制面板")
    st.button("＋ 新建对话", on_click=start_new_chat, use_container_width=True)
    st.markdown("---")

    if st.session_state["conversations"]:
        st.markdown("### 历史记录")
        for cid, conv in st.session_state["conversations"].items():
            is_active = cid == st.session_state["session_id"]
            cls = "sidebar-chat-item active" if is_active else "sidebar-chat-item"
            st.markdown(
                f'<div class="{cls}">💬 {conv["title"]}</div>',
                unsafe_allow_html=True,
            )

    st.markdown("---")
    st.markdown(
        '<div style="text-align:center; color:#666680; font-size:11px; padding:12px 0;">'
        "Powered by ReAct Agent<br>© 2026 智能客服系统"
        "</div>",
        unsafe_allow_html=True,
    )

# ── Main chat area ──
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
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    st.session_state["messages"].append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("正在思考..."):
            res_stream = st.session_state["agent"].excute_stream(prompt)
            st.write_stream(stream_capture(res_stream))

    full_response = st.session_state.get("_last_full_response", "")
    if full_response:
        st.session_state["messages"].append({"role": "assistant", "content": full_response})
