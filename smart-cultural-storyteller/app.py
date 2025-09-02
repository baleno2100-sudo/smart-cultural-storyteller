import streamlit as st
import requests

# ================= CONFIG =================
st.set_page_config(page_title="Smart Cultural Storyteller", page_icon="✨", layout="centered")

OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
MODEL = "openai/gpt-4o-mini"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
# ===========================================

# ======== Theme Config ========
if "theme" not in st.session_state:
    st.session_state["theme"] = "dark"

# Sidebar Theme Toggle (Button)
if st.sidebar.button("Toggle Theme"):
    st.session_state["theme"] = (
        "light" if st.session_state["theme"] == "dark" else "dark"
    )

# Colors based on theme
if st.session_state["theme"] == "dark":
    bg_color = "#222222"
    text_color = "#FFFFFF"
    accent_color = "#FF9800"
    story_bg = "#1e1e1e"
    story_text_color = "#FFFFFF"
    scrollbar_color = "#888888"
else:
    bg_color = "#e0bfbf"
    text_color = "#000000"
    accent_color = "#4CAF50"
    story_bg = "#f9f9f9"
    story_text_color = "#000000"
    scrollbar_color = "#333333"

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
st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
        }}
        .stButton button {{
            background-color: {accent_color};
            color: white;
            font-weight: bold;
            border-radius: 10px;
        }}
        .story-box {{
            max-height: 400px;
            overflow-y: auto;
            padding: 15px;
            background-color: {story_bg};
            border: 1px solid {accent_color};
            border-radius: 10px;
            color: {story_text_color};
            white-space: pre-wrap;
            line-height: 1.6;
        }}
        .story-box::-webkit-scrollbar {{
            width: 10px;
        }}
        .story-box::-webkit-scrollbar-thumb {{
            background-color: {scrollbar_color};
            border-radius: 5px;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🌍 Smart Cultural Storyteller")
st.markdown("Retell **Folk Tales**, **Historical Events**, and **Traditions** with AI magic ✨")

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

# Show story inside proper box
if st.session_state["story"]:
    st.subheader("📖 Your Story:")

    st.markdown(
        f"""
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
