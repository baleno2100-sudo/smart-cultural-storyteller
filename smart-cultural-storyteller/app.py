import streamlit as st
import requests
import io
import datetime
import re
import sqlite3
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# ================= CONFIG =================
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
MODEL = "openai/gpt-4o-mini"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
accent_color = "#FFA500"  # Orange for titles
# ===========================================

st.set_page_config(page_title="Smart Cultural Storyteller", page_icon="🎭", layout="centered")

# ======== Theme State ========
if "theme" not in st.session_state:
    st.session_state["theme"] = "dark"

# ======== Sidebar Theme Toggle ========
st.sidebar.title("Theme")
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("🌞 Light"):
        st.session_state["theme"] = "light"
with col2:
    if st.button("🌙 Dark"):
        st.session_state["theme"] = "dark"

# ======== SQLite Database Setup ========
conn = sqlite3.connect("stories.db", check_same_thread=False)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS stories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    story TEXT,
    moral TEXT,
    category TEXT,
    prompt TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# ======== Theme Styling ========
def apply_theme():
    if st.session_state["theme"] == "dark":
        story_bg = "#1e1e1e"
        story_text_color = "#FFFFFF"
        scrollbar_thumb = "#888"
        scrollbar_track = "#333"
        app_bg = "#222222"
        button_color = accent_color
    else:
        story_bg = "#f9f9f9"
        story_text_color = "#000000"
        scrollbar_thumb = "#555"
        scrollbar_track = "#DDD"
        app_bg = "#FFFFFF"
        button_color = accent_color

    st.markdown(
        f"""
        <style>
            .stApp {{background-color: {app_bg}; color: {story_text_color};}}
            .stButton button {{
                background-color: {button_color};
                color: white;
                font-weight: bold;
                border-radius: 10px;
            }}
            .story-box {{
                overflow-y: auto;
                padding: 12px;
                background-color: {story_bg};
                border: 1px solid {accent_color};
                border-radius: 10px;
                color: {story_text_color};
                scrollbar-width: thin; 
                scrollbar-color: {scrollbar_thumb} {scrollbar_track};
                scroll-behavior: smooth;
            }}
            .story-box::-webkit-scrollbar {{
                width: 8px;
            }}
            .story-box::-webkit-scrollbar-track {{
                background: {scrollbar_track};
                border-radius: 8px;
            }}
            .story-box::-webkit-scrollbar-thumb {{
                background-color: {scrollbar_thumb};
                border-radius: 10px;
                border: 2px solid {scrollbar_track};
            }}
            .story-card {{
                background-color: {story_bg};
                border: 1px solid {accent_color};
                border-radius: 10px;
                padding: 12px;
                margin-bottom: 8px;
                cursor: pointer;
            }}
        </style>
        """,
        unsafe_allow_html=True
    )

apply_theme()

# ======== Story Generation Function ========
def generate_story(prompt, category):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    story_type = {
        "Folk Tale": "You are a magical storyteller. Retell folk tales in a vivid, enchanting, and interactive way. Make sure the story is at least 500 words long with dialogues, plot, and rich details.",
        "Historical Event": "You are a historian. Retell historical events in an engaging and detailed storytelling manner. Include context, characters, and vivid descriptions.",
        "Tradition": "You are a cultural guide. Explain traditions with stories and meaning in a detailed and captivating way."
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": story_type.get(category, story_type["Folk Tale"])},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1500,
        "temperature": 0.8,
        "stream": False
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return f"Error: {response.status_code} - {response.text}"

# ======== Generate Story with Title and Moral ========
def generate_story_with_title(prompt, category):
    full_prompt = (
        f"{prompt}\n\n"
        "Also provide:\n"
        "1. A short, catchy title for this story.\n"
        "2. The moral of the story in one sentence.\n"
        "Return the result in this format:\n"
        "TITLE: <title>\n"
        "STORY:\n<story text>\n"
        "MORAL: <moral text>"
    )
    response_text = generate_story(full_prompt, category)
    
    title, story, moral = "Untitled Story", "", ""
    if "TITLE:" in response_text and "STORY:" in response_text and "MORAL:" in response_text:
        try:
            title = response_text.split("TITLE:")[1].split("STORY:")[0].strip()
            story = response_text.split("STORY:")[1].split("MORAL:")[0].strip()
            moral = response_text.split("MORAL:")[1].strip()
        except Exception:
            story = response_text
    else:
        story = response_text

    return title, story, moral

# ======== Save Story to Database ========
def save_story(title, story, moral, category, prompt):
    c.execute("INSERT INTO stories (title, story, moral, category, prompt) VALUES (?, ?, ?, ?, ?)",
              (title, story, moral, category, prompt))
    conn.commit()

# ======== Session State ========
for key in ["story", "story_title", "moral", "prompt"]:
    if key not in st.session_state:
        st.session_state[key] = ""

# ======== Story Generation Callback ========
def trigger_story_generation():
    if not st.session_state["prompt"].strip():
        st.warning("⚠️ Please enter a prompt first!")
    else:
        with st.spinner("Summoning your story... 🌌"):
            title, story, moral = generate_story_with_title(st.session_state["prompt"], category)
            st.session_state["story_title"] = title
            st.session_state["story"] = story
            st.session_state["moral"] = moral
            save_story(title, story, moral, category, st.session_state["prompt"])

# ======== Prompt Input ========
st.title("🎭 Smart Cultural Storyteller")
st.markdown("Retell **Folk Tales**, **Historical Events**, and **Traditions** with AI magic ✨")
st.text_input("Enter a prompt to begin your story:", key="prompt", on_change=trigger_story_generation)

if st.button("Generate Story"):
    trigger_story_generation()

# ======== Feature Stories ========
st.header("🌟 Featured Stories")
c.execute("SELECT id, title FROM stories ORDER BY created_at DESC LIMIT 20")
rows = c.fetchall()

def clean_title(title):
    # Remove any HTML tags or formatting
    return re.sub(r"<.*?>", "", title).strip()

for row in rows:
    story_id, title = row
    clean_story_title = clean_title(title)
    with st.expander("", expanded=False):
        st.markdown(f"<p style='font-weight:bold; color:{accent_color}; font-size:18px;'>{clean_story_title}</p>", unsafe_allow_html=True)
        c.execute("SELECT story, moral FROM stories WHERE id=?", (story_id,))
        story_data = c.fetchone()
        story_text, moral_text = story_data if story_data else ("", "")
        st.markdown(f"{story_text.replace(chr(10), '<br>')}", unsafe_allow_html=True)
        if moral_text:
            st.markdown(f"<p style='font-weight:bold; color:{accent_color}; margin-top:12px;'>Moral: {moral_text}</p>", unsafe_allow_html=True)
