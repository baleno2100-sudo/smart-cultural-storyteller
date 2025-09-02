import streamlit as st
from io import BytesIO

# Set page configuration (MUST be first Streamlit command)
st.set_page_config(page_title="Smart Cultural Storyteller", page_icon="✨", layout="centered")

# --- Category icons ---
CATEGORY_ICONS = {
    "Folk Tale": "🧙",
    "History": "🏰",
    "Tradition": "🎎"
}

# --- Initialize session state ---
if "story" not in st.session_state:
    st.session_state.story = ""
if "theme" not in st.session_state:
    st.session_state.theme = "light"

# --- Theme toggle ---
col1, col2 = st.columns([5,1])
with col2:
    if st.button("🌙" if st.session_state.theme == "light" else "☀️", help="Toggle light/dark theme"):
        st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"

# --- Accent colors ---
if st.session_state.theme == "dark":
    bg_color = "#1E1E1E"
    text_color = "#F1F1F1"
    border_color = "#555"
    button_color = "#444"
    button_text = "#FFF"
else:
    bg_color = "#FAFAFA"
    text_color = "#000"
    border_color = "#DDD"
    button_color = "#E0E0E0"
    button_text = "#000"

st.markdown(
    f"""
    <style>
    .scroll-box {{
        max-height: 400px;
        overflow-y: auto;
        padding: 1rem;
        border: 1px solid {border_color};
        border-radius: 0.5rem;
        background-color: {bg_color};
        color: {text_color};
    }}
    .scroll-box::-webkit-scrollbar {{
        width: 8px;
    }}
    .scroll-box::-webkit-scrollbar-thumb {{
        background: {border_color};
        border-radius: 4px;
    }}
    .stDownloadButton button, .stButton button {{
        background-color: {button_color} !important;
        color: {button_text} !important;
        border-radius: 0.5rem !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("✨ Smart Cultural Storyteller")

# --- Category selection ---
category = st.selectbox("Choose a category:", list(CATEGORY_ICONS.keys()), format_func=lambda x: f"{CATEGORY_ICONS[x]} {x}")

# --- Story input ---
prompt = st.text_area("Enter a topic or prompt for your story:", "")

# --- Generate story button ---
if st.button("Generate New Story"):
    if prompt.strip():
        st.session_state.story = f"<b>{CATEGORY_ICONS[category]} {category}</b><br><br>This is a sample story about <b>{prompt}</b>. " \
                                 f"It will be dynamically generated in your real app."
    else:
        st.warning("Please enter a topic before generating a story!")

# --- Show existing story ---
if st.session_state.story:
    st.subheader("📖 Your Story:")
    st.markdown(f'<div class="scroll-box">{st.session_state.story}</div>', unsafe_allow_html=True)

    # Download story as text file
    story_bytes = BytesIO(st.session_state.story.encode('utf-8'))
    st.download_button(
        label="⬇️ Download Story",
        data=story_bytes,
        file_name="story.txt",
        mime="text/plain"
    )
