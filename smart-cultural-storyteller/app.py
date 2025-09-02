import streamlit as st
import requests
from io import BytesIO

# =============== CONFIG ===============
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
MODEL = "openai/gpt-4o-mini"   # Can be replaced with any OpenRouter-supported model
API_URL = "https://openrouter.ai/api/v1/chat/completions"
# =====================================

st.set_page_config(page_title="Smart Cultural Storyteller", page_icon="✨", layout="centered")

# ---------- SESSION STATE ----------
if "theme" not in st.session_state:
    st.session_state.theme = "light"
if "story" not in st.session_state:
    st.session_state.story = ""

# ---------- THEME TOGGLE ----------
def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"

st.sidebar.button("🌗 Toggle Theme", on_click=toggle_theme)

# ---------- COLOR SCHEME ----------
is_dark = st.session_state.theme == "dark"
primary_btn_bg = "#ff9800" if not is_dark else "#2196f3"
primary_btn_text = "#000000" if not is_dark else "#ffffff"

# ---------- GENERATE STORY FUNCTION ----------
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
        data = response.json()
        return data['choices'][0]['message']['content']
    else:
        return f"Error: {response.status_code} - {response.text}"

# ---------- UI HEADER ----------
st.title("🌍 Smart Cultural Storyteller")
st.markdown("Retell **Folk Tales**, **Historical Events**, and **Traditions** with AI magic ✨")

# ---------- CATEGORY WITH ICONS ----------
st.sidebar.header("Choose a Category")
category_icons = {
    "Folk Tale": "📖",
    "Historical Event": "🏰",
    "Tradition": "🎎"
}
category = st.sidebar.radio(
    "Pick one:",
    ["Folk Tale", "Historical Event", "Tradition"],
    format_func=lambda c: f"{category_icons[c]} {c}"
)

# ---------- PROMPT INPUT ----------
prompt = st.text_input("Enter a prompt to begin your story:")

# ---------- BUTTON STYLING ----------
def themed_button(label, key=None):
    return st.markdown(
        f"""
        <style>
        div.stButton > button:first-child {{
            background-color: {primary_btn_bg};
            color: {primary_btn_text};
            border-radius: 8px;
            padding: 0.5rem 1rem;
            border: none;
            font-weight: bold;
        }}
        div.stButton > button:first-child:hover {{
            opacity: 0.9;
        }}
        </style>
        """,
        unsafe_allow_html=True
    ) or st.button(label, key=key)

# ---------- STORY GENERATION ----------
if st.button("Generate Story"):
    if not prompt:
        st.warning("⚠️ Please enter a prompt first!")
    else:
        with st.spinner("Summoning your story... 🌌"):
            story = generate_story(prompt, category)
            st.session_state.story = story

# ---------- SHOW STORY ----------
if st.session_state.story:
    st.subheader("📖 Your Story:")
    box_bg = "#1E1E1E" if is_dark else "#fafafa"
    box_border = "#555" if is_dark else "#ddd"
    box_text = "#f1f1f1" if is_dark else "#000"

    st.markdown(
        f"""
        <div style="
            max-height: 400px; 
            overflow-y: auto; 
            padding: 1rem; 
            border: 1px solid {box_border}; 
            border-radius: 0.5rem; 
            background-color: {box_bg};
            color: {box_text};
        ">
            {st.session_state.story}
        </div>
        """,
        unsafe_allow_html=True
    )

    # Download story button
    story_bytes = BytesIO(st.session_state.story.encode("utf-8"))
    st.download_button(
        "📥 Download Story",
        story_bytes,
        file_name="story.txt",
        mime="text/plain",
        use_container_width=True
    )

    # Generate new story button
    if st.button("✨ Generate New Story"):
        st.session_state.story = ""
        st.experimental_rerun()
