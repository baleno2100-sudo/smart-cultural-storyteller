import streamlit as st
import requests
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER
from datetime import datetime

# ================= CONFIG =================
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
MODEL = "openai/gpt-4o-mini"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
# ===========================================

st.set_page_config(page_title="Smart Cultural Storyteller", page_icon="🎭", layout="centered")

# ======== Theme State ========
if "theme" not in st.session_state:
    st.session_state["theme"] = "dark"

# Button to toggle theme
if st.sidebar.button("Toggle Theme"):
    st.session_state["theme"] = "light" if st.session_state["theme"] == "dark" else "dark"

accent_color = "#FF9800"  # Keep UI dark overall

# ======== Story Function ========
def generate_story(prompt, category):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    story_type = {
        "Folk Tale": "You are a magical storyteller. Retell folk tales in a vivid, enchanting, interactive, and detailed way. Make the story at least 500 words long.",
        "Historical Event": "You are a historian. Retell history with engaging storytelling, rich details, and vivid narrative. Ensure at least 500 words.",
        "Tradition": "You are a cultural guide. Explain traditions with stories, meaning, and rich details. Minimum 500 words."
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

# ======== Story Box Styling ========
if st.session_state["theme"] == "dark":
    story_bg = "#1e1e1e"
    story_text_color = "#FFFFFF"
    scrollbar_color = "#888"
else:
    story_bg = "#f9f9f9"
    story_text_color = "#000000"
    scrollbar_color = "#333"  # Dark scrollbar in light theme

st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: #222222;  /* Always dark */
            color: #FFFFFF;
        }}
        .stButton button {{
            background-color: {accent_color};
            color: white;
            font-weight: bold;
            border-radius: 10px;
        }}
        .story-box {{
            overflow-y: auto;
            padding: 10px;
            background-color: {story_bg};
            border: 1px solid {accent_color};
            border-radius: 8px;
            color: {story_text_color};
        }}
        .story-box::-webkit-scrollbar {{
            width: 10px;
        }}
        .story-box::-webkit-scrollbar-thumb {{
            background-color: {scrollbar_color};
            border-radius: 10px;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# ======== App UI ========
st.title("🎭 Smart Cultural Storyteller")
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

# Show previous story preview
if st.session_state["story"]:
    st.subheader("📖 Your Story:")

    # Split title and body
    story_lines = st.session_state["story"].split("\n")
    title = story_lines[0].strip()
    body_lines = story_lines[1:]

    story_html = f"<div style='text-align:center; font-weight:bold; font-size:18px; margin-bottom:10px;'>{title}</div>"
    story_html += "<br>".join(body_lines)

    st.markdown(f"<div class='story-box'>{story_html}</div>", unsafe_allow_html=True)

    # ===== Download as TXT =====
    st.download_button(
        "Download Story (TXT)",
        data=st.session_state["story"].encode("utf-8"),
        file_name="story.txt",
        mime="text/plain",
        key="download-txt"
    )

    # ===== Download as PDF =====
    def create_pdf(story_text):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                rightMargin=40, leftMargin=40,
                                topMargin=60, bottomMargin=40)
        styles = getSampleStyleSheet()
        story = []

        # Extract title
        lines = story_text.split("\n")
        title_text = lines[0].strip()
        body_text = "\n".join(lines[1:])

        # Title style
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=18)
        story.append(Paragraph(title_text, title_style))
        story.append(Spacer(1, 12))

        # Body style
        body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=12, leading=16)
        for para in body_text.split("\n\n"):
            story.append(Paragraph(para.strip(), body_style))
            story.append(Spacer(1, 12))

        # Footer
        footer_style = ParagraphStyle('FooterStyle', parent=styles['Normal'], alignment=TA_CENTER, fontSize=9, textColor="#888888")
        story.append(Spacer(1, 24))
        story.append(Paragraph(f"Generated by Smart Cultural Storyteller | {datetime.now().strftime('%Y-%m-%d')}", footer_style))

        doc.build(story)
        buffer.seek(0)
        return buffer

    pdf_buffer = create_pdf(st.session_state["story"])
    st.download_button(
        "Download Story (PDF)",
        data=pdf_buffer,
        file_name="story.pdf",
        mime="application/pdf",
        key="download-pdf"
    )
