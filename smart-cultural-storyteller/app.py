import streamlit as st
import requests

# ================= CONFIG =================
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
MODEL = "openai/gpt-4o-mini"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
# ===========================================

# ======== Theme State ========
if "story_theme" not in st.session_state:
    st.session_state["story_theme"] = "dark"  # default dark

def toggle_story_theme():
    st.session_state["story_theme"] = (
        "light" if st.session_state["story_theme"] == "dark" else "dark"
    )

# ======== Story Function ========
def generate_story(prompt, category):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    story_type = {
        "Folk Tale": "You are a magical storyteller. Retell folk tales in a vivid, enchanting, and interactive way.",
        "Historical Event": "You are a historian. Retell history with engaging storytelling.",
        "Tradition": "You are a cultural guide. Explain traditions with stories and meaning."
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": story_type.get(category, story_type["Folk Tale"])},
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return f"Error: {response.status_code} - {response.text}"

# ======== Streamlit UI ========
st.set_page_config(page_title="Smart Cultural Storyteller", page_icon="✨", layout="centered")

# Always dark background for app
st.markdown(
    """
    <style>
        .stApp {
            background-color: #121212;
            color: #FFFFFF;
        }
        .stButton button {
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: bold;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🌍 Smart Cultural Storyteller")
st.markdown("Retell **Folk Tales**, **Historical Events**, and **Traditions** with AI magic ✨")

# Sidebar with icons for toggle
st.sidebar.header("Theme Controls")
if st.sidebar.button("🌙" if st.session_state["story_theme"] == "dark" else "☀️"):
    toggle_story_theme()

# Sidebar Category
st.sidebar.header("Choose a Category")
category = st.sidebar.radio(
    "Pick one:",
    ["Folk Tale", "Historical Event", "Tradition"],
    format_func=lambda x: f"🌟 {x}" if x == "Folk Tale" else ("📜 "+x if x=="Historical Event" else "🎎 "+x)
)

# User input
prompt = st.text_input("Enter a prompt to begin your story:")

# Story handling
if "story" not in st.session_state:
    st.session_state["story"] = ""

if st.button("Generate Story"):
    if not prompt:
        st.warning("⚠️ Please enter a prompt first!")
    else:
        with st.spinner("Summoning your story... 🌌"):
            story = generate_story(prompt, category)
            st.session_state["story"] = story

# Story box styling (toggle applied here only)
if st.session_state["story_theme"] == "dark":
    story_bg = "#1e1e1e"
    story_text = "#FFFFFF"
    scrollbar = "#555555"
else:
    story_bg = "#FFFFFF"
    story_text = "#000000"
    scrollbar = "#222222"

if st.session_state["story"]:
    st.subheader("📖 Your Story:")
    st.markdown(
        f"""
        <style>
            .story-box {{
                background-color: {story_bg};
                color: {story_text};
                padding: 15px;
                border-radius: 10px;
                max-height: 400px;
                overflow-y: auto;
                border: 1px solid #888;
            }}
            .story-box::-webkit-scrollbar {{
                width: 8px;
            }}
            .story-box::-webkit-scrollbar-thumb {{
                background-color: {scrollbar};
                border-radius: 10px;
            }}
        </style>
        <div class="story-box">{st.session_state['story']}</div>
        """,
        unsafe_allow_html=True
    )
    st.download_button(
        "Download Story",
        data=st.session_state["story"].encode("utf-8"),
        file_name="story.txt",
        mime="text/plain",
        key="download-btn"
    )
