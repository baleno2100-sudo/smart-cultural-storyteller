import streamlit as st
import requests
import base64

# ================== CONFIG ==================
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
MODEL = "openai/gpt-4o-mini"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
# ============================================

# --------- Utility: Call OpenRouter API ---------
def generate_story(prompt, category):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    story_type = {
        "Folk Tale": "You are a magical storyteller. Retell folk tales vividly and interactively.",
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

# --------- Utility: Download link for story ---------
def get_download_link(text, filename):
    b64 = base64.b64encode(text.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{filename}" style="text-decoration:none;"><button>📥 Download Story</button></a>'

# --------- Streamlit Page Setup ---------
st.set_page_config(page_title="Smart Cultural Storyteller", page_icon="✨", layout="centered")

# --------- Session State ---------
if "story" not in st.session_state:
    st.session_state.story = ""
if "theme" not in st.session_state:
    st.session_state.theme = "light"

# --------- Theme Toggle ---------
is_dark = st.session_state.theme == "dark"
theme_toggle = st.sidebar.checkbox("🌙 Dark M_
