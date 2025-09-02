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

# ================= DATABASE =================
conn = sqlite3.connect("stories.db", check_same_thread=False)
c = conn.cursor()
c.execute("""
    CREATE TABLE IF NOT EXISTS stories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        category TEXT,
        story TEXT,
        moral TEXT,
        prompt TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
conn.commit()

def save_story(title, category, story, moral, prompt):
    c.execute("""
        INSERT INTO stories (title, category, story, moral, prompt)
        VALUES (?, ?, ?, ?, ?)
    """, (title, category, story, moral, prompt))
    conn.commit()

def get_all_stories(category_filter="All"):
    if category_filter == "All":
        c.execute("SELECT * FROM stories ORDER BY created_at DESC")
    else:
        c.execute("SELECT * FROM stories WHERE category=? ORDER BY created_at DESC", (category_filter,))
    return c.fetchall()

# ================= THEME =================
if "theme" not in st.session_state:
    st.session_state["theme"] = "dark"

st.sidebar.title("Theme")
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("🌞 Light"):
        st.session_state["theme"] = "light"
with col2:
    if st.button("🌙 Dark"):
        st.session_state["theme"] = "dark"

def apply_theme():
    if st.session_state["theme"] == "dark":
        story_bg = "#1e1e1e"
        story_text_color = "#FFFFFF"
        scrollbar_thumb = "#888"
        scrollbar_track = "#333"
        app_bg = "#222222"
        button_text = "#FFFFFF"
    else:
        story_bg = "#f9f9f9"
        story_text_color = "#000000"
        scrollbar_thumb = "#555"
        scrollbar_track = "#DDD"
        app_bg = "#FFFFFF"
        button_text = "#000000"

    st.markdown(f"""
        <style>
            .stApp {{background-color: {app_bg}; color: {story_text_color};}}
            .stButton button {{
                background-color: {accent_color};
                color: {button_text};
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

# ================= STORY GENERATION =================
def generate_story(prompt, category):
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
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
        f"{prompt}\n\nAlso provide:\n"
        "1. A short, catchy title for this story.\n"
        "2. The moral of the story in one sentence.\n"
        "Return the result in this format:\n"
        "TITLE: <title>\nSTORY:\n<story text>\nMORAL: <moral text>"
    )
    response_text = generate_story(full_prompt, category)
    title, story, moral = "Untitled Story", "", ""
    if "TITLE:" in response_text and "STORY:" in response_text and "MORAL:" in response_text:
        try:
            title = response_text.split("TITLE:")[1].split("STORY:")[0].strip()
            story = response_text.split("STORY:")[1].split("MORAL:")[0].strip()
            moral = response_text.split("MORAL:")[1].strip()
        except:
            story = response_text
    else:
        story = response_text
    return title, story, moral

# ================= PDF EXPORT =================
def add_footer(canvas, doc):
    footer_text = f"Generated by Smart Cultural Storyteller – {datetime.date.today().strftime('%b %d, %Y')}"
    canvas.setFont("Helvetica-Oblique", 9)
    canvas.setFillColor(colors.HexColor(accent_color))
    canvas.drawCentredString(letter[0] / 2.0, 30, footer_text)

def create_pdf(story_text):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleStyle", parent=styles["Heading1"],
                                 fontName="Helvetica-Bold", fontSize=20,
                                 textColor=colors.HexColor(accent_color), alignment=1, spaceAfter=6)
    body_style = ParagraphStyle("BodyStyle", parent=styles["Normal"], fontName="Helvetica", fontSize=12, leading=16)
    moral_style = ParagraphStyle("MoralStyle", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=12,
                                 leading=16, textColor=colors.HexColor(accent_color), spaceBefore=12)

    if "\n\nMoral:" in story_text:
        parts = story_text.split("\n\nMoral:")
        story_body = parts[0]
        moral = parts[1].strip()
    else:
        story_body = story_text
        moral = ""

    story_elements = [Paragraph(story_body.split("\n")[0], title_style), Spacer(1, 6)]
    for line in story_body.split("\n")[1:]:
        if line.strip():
            story_elements.append(Paragraph(line.strip(), body_style))
            story_elements.append(Spacer(1, 4))

    if moral:
        story_elements.append(Paragraph("Moral: " + moral, moral_style))

    doc.build(story_elements, onFirstPage=add_footer, onLaterPages=add_footer)
    buffer.seek(0)
    return buffer

def sanitize_filename(title):
    sanitized = re.sub(r'[\\/:"*?<>|]+', '', title).strip()
    if not sanitized:
        sanitized = "story"
    return sanitized + ".pdf"

# ================= UI =================
st.title("🎭 Smart Cultural Storyteller")
st.markdown("Retell **Folk Tales**, **Historical Events**, and **Traditions** with AI magic ✨")

# Sidebar Category
st.sidebar.header("Choose a Category")
category = st.sidebar.radio(
    "Pick one:",
    ["Folk Tale", "Historical Event", "Tradition"],
    format_func=lambda x: f"🌟 {x}" if x == "Folk Tale" else ("📜 "+x if x=="Historical Event" else "🎎 "+x)
)

# Session State
for key in ["story", "story_title", "moral", "prompt"]:
    if key not in st.session_state:
        st.session_state[key] = ""

# Story Generation Callback
def trigger_story_generation():
    if not st.session_state["prompt"].strip():
        st.warning("⚠️ Please enter a prompt first!")
    else:
        with st.spinner("Summoning your story... 🌌"):
            title, story, moral = generate_story_with_title(st.session_state["prompt"], category)
            st.session_state["story_title"] = title
            st.session_state["story"] = story
            st.session_state["moral"] = moral
            save_story(title, category, story, moral, st.session_state["prompt"])

# Prompt Input
st.text_input("Enter a prompt to begin your story:", key="prompt", on_change=trigger_story_generation)
if st.button("Generate Story"):
    trigger_story_generation()

# Story Display
if st.session_state["story"]:
    story_lines = st.session_state["story"].split("\n")
    story_height = min(800, max(400, 30 * len(story_lines)))
    st.markdown(f"<style>.story-box {{height: {story_height}px;}}</style>", unsafe_allow_html=True)
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

    full_text = f"{st.session_state.get('story_title','')}\n\n{st.session_state['story']}\n\nMoral: {st.session_state.get('moral','')}"
    st.download_button("📥 Download as TXT", data=full_text.encode("utf-8"), file_name="story.txt", mime="text/plain")
    pdf_buffer = create_pdf(full_text)
    pdf_filename = sanitize_filename(st.session_state.get("story_title", "story"))
    st.download_button("📥 Download as PDF", data=pdf_buffer, file_name=pdf_filename, mime="application/pdf")

# ================= Featured Stories =================
st.markdown("---")
st.subheader("📚 Featured Stories")
filter_option = st.selectbox("Filter by category:", ["All", "Folk Tale", "Historical Event", "Tradition"])
stories = get_all_stories(filter_option)

if stories:
    st.markdown(f"""
        <style>
        .story-card {{
            background-color: {accent_color}10;
            border: 2px solid {accent_color};
            border-radius: 12px;
            padding: 12px 18px;
            margin-bottom: 12px;
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
        }}
        .story-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            background-color: {accent_color}20;
        }}
        .story-title {{
            font-size: 18px;
            font-weight: bold;
            color: {accent_color};
            margin: 0;
        }}
        </style>
    """, unsafe_allow_html=True)

    for s in stories:
        story_id, title, cat, story_text, moral, prompt_text, created_at = s
        with st.expander(f"<div class='story-card'><p class='story-title'>{title}</p></div>", expanded=False):
            st.markdown(f"**Category:** {cat}")
            st.markdown(f"**Prompt:** {prompt_text}")
            st.markdown(f"{story_text}")
            st.markdown(f"**Moral:** {moral}")
else:
    st.info("No stories found yet!")
