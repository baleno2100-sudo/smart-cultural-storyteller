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
accent_color = "#FF9800"  # Orange accent
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

# ======== Sidebar Navigation ========
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to:", ["Generate Story", "Featured Stories"])

# ======== SQLite Setup ========
conn = sqlite3.connect('stories.db')
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS stories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    category TEXT,
    story TEXT,
    moral TEXT,
    prompt TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()
conn.close()

# ======== Story Functions ========
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

def save_story_to_db(title, category, story, moral, prompt):
    conn = sqlite3.connect('stories.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO stories (title, category, story, moral, prompt)
        VALUES (?, ?, ?, ?, ?)
    ''', (title, category, story, moral, prompt))
    conn.commit()
    conn.close()

def get_all_stories(filter_category="All"):
    conn = sqlite3.connect('stories.db')
    c = conn.cursor()
    if filter_category == "All":
        c.execute("SELECT * FROM stories ORDER BY created_at DESC")
    else:
        c.execute("SELECT * FROM stories WHERE category=? ORDER BY created_at DESC", (filter_category,))
    stories = c.fetchall()
    conn.close()
    return stories

# ======== Theme Styling ========
def apply_theme():
    if st.session_state["theme"] == "dark":
        story_bg = "#1e1e1e"
        story_text_color = "#FFFFFF"
        scrollbar_thumb = "#888"
        scrollbar_track = "#333"
        app_bg = "#222222"
        app_text = "#FFFFFF"
    else:
        story_bg = "#f9f9f9"
        story_text_color = "#000000"
        scrollbar_thumb = "#555"
        scrollbar_track = "#DDD"
        app_bg = "#FFF"
        app_text = "#000000"

    st.markdown(f"""
        <style>
        .stApp {{background-color: {app_bg}; color: {app_text};}}
        .stButton button {{
            background-color: {accent_color};
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
        </style>
    """, unsafe_allow_html=True)

apply_theme()

# ======== Generate Story Page ========
if page == "Generate Story":
    st.title("🎭 Smart Cultural Storyteller")
    st.markdown("Retell **Folk Tales**, **Historical Events**, and **Traditions** with AI magic ✨")

    # Sidebar Category
    st.sidebar.header("Choose a Category")
    category = st.sidebar.radio(
        "Pick one:",
        ["Folk Tale", "Historical Event", "Tradition"],
        format_func=lambda x: f"🌟 {x}" if x == "Folk Tale" else ("📜 "+x if x=="Historical Event" else "🎎 "+x)
    )

    if "prompt" not in st.session_state:
        st.session_state["prompt"] = ""
    if "story" not in st.session_state:
        st.session_state["story"] = ""
    if "story_title" not in st.session_state:
        st.session_state["story_title"] = ""
    if "moral" not in st.session_state:
        st.session_state["moral"] = ""

    def trigger_story_generation():
        if not st.session_state["prompt"].strip():
            st.warning("⚠️ Please enter a prompt first!")
        else:
            with st.spinner("Summoning your story... 🌌"):
                title, story, moral = generate_story_with_title(st.session_state["prompt"], category)
                st.session_state["story_title"] = title
                st.session_state["story"] = story
                st.session_state["moral"] = moral
                save_story_to_db(title, category, story, moral, st.session_state["prompt"])

    st.text_input("Enter a prompt to begin your story:", key="prompt", on_change=trigger_story_generation)
    if st.button("Generate Story"):
        trigger_story_generation()

    # Story display
    if st.session_state["story"]:
        story_html = f"""
        <div class='story-box'>
            <h2 style='text-align:center; color:{accent_color}; font-size:20px; margin-bottom:6px;'>
                {st.session_state.get('story_title', '')}
            </h2>
            {st.session_state['story'].replace('\n', '<br>')}
            <p style='font-weight:bold; color:{accent_color}; margin-top:12px;'>
                Moral: {st.session_state.get('moral', '')}
            </p>
        </div>
        """
        st.subheader("📖 Your Story:")
        st.markdown(story_html, unsafe_allow_html=True)

# ======== Featured Stories Page ========
else:
    st.subheader("📚 Featured Stories")
    filter_option = st.selectbox("Filter by category:", ["All", "Folk Tale", "Historical Event", "Tradition"])
    stories = get_all_stories(filter_option)

    if stories:
        for s in stories:
            story_id, title, cat, story_text, moral, prompt_text, created_at = s
            with st.expander(f"📖 {title} ({cat}) - Moral: {moral[:60]}{'...' if len(moral)>60 else ''}"):
                st.markdown(f"**Prompt:** {prompt_text}")
                st.markdown(f"{story_text}")
                st.markdown(f"**Moral:** {moral}")
    else:
        st.info("No stories found yet!")
