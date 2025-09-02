import streamlit as st
import requests

# ================= CONFIG =================
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
MODEL = "openai/gpt-4o-mini"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
# ===========================================

# ======== Theme State ========
if "story_theme" not in st.session_state:
    st.session_state["story_theme"] = "dark"

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

# Global app always dark
st.markdown(
    """
    <style>
        .stApp {
            background-color: #111111;
            color: #FFFFFF;
        }
        .stButton button {
            background-color: #444444;
            color: white;
            font-weight: bold;
            border-radius: 8px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🌍 Smart Cultural Storyteller")
st.markdown("Retell **Folk Tales**, **Historical Events**, and **Traditions** with AI magic ✨")

# Sidebar Category + Theme toggle
st.sidebar.header("Options")
if st.sidebar.button("🌙 / ☀️ Toggle Story Theme"):
    toggle_story_theme()

category = st.sidebar.radio(
    "Choose a Category:",
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

# Story Box Styles
if st.session_state["story_theme"] == "dark":
    story_bg = "#222222"
    story_text = "#FFFFFF"
    scrollbar_color = "#888888"
else:
    story_bg = "#FFFFFF"
    story_text = "#000000"
    scrollbar_color = "#333333"

# Show story with scrollable box
if st.session_state["story"]:
    st.subheader("📖 Your Story:")
    st.markdown(
        f"""
        <style>
            .story-box {{
                background-color: {story_bg};
                color: {story_text};
                max-height: 400px;
                overflow-y: auto;
                padding: 10px;
                border: 1px solid #666;
                border-radius: 8px;
            }}
            .story-box::-webkit-scrollbar {{
                width: 8px;
            }}
            .story-box::-webkit-scrollbar-thumb {{
                background-color: {scrollbar_color};
                border-radius: 4px;
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
        mime="text/plain"
    )
