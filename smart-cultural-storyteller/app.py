import streamlit as st
import requests
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from io import BytesIO

# ================= CONFIG =================
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
MODEL = "openai/gpt-4o-mini"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
# ===========================================

# 🚨 MUST be first Streamlit call
st.set_page_config(page_title="Smart Cultural Storyteller", page_icon="🎭", layout="centered")

# ======== Theme State ========
if "theme" not in st.session_state:
    st.session_state["theme"] = "dark"

# Button to toggle theme
if st.sidebar.button("Toggle Theme"):
    st.session_state["theme"] = "light" if st.session_state["theme"] == "dark" else "dark"

accent_color = "#FF9800"  # Accent for buttons/borders

# ======== Story Function ========
def generate_story(prompt, category):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    story_type = {
        "Folk Tale": "You are a magical storyteller. Retell folk tales in a vivid, enchanting, interactive, and detailed way. Ensure the story is at least 500 words with rich dialogues and events.",
        "Historical Event": "You are a historian. Retell historical events with engaging storytelling, including detailed context and characters. Make it at least 500 words.",
        "Tradition": "You are a cultural guide. Explain traditions with stories and meaning, making them detailed and vivid. Minimum 500 words."
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
    scrollbar_thumb = "#888"
else:
    story_bg = "#f9f9f9"
    story_text_color = "#000000"
    scrollbar_thumb = "#333"  # Dark scrollbar for light theme

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
            background-color: {scrollbar_thumb};
            border-radius: 10px;
        }}
        .story-box::-webkit-scrollbar-track {{
            background-color: transparent;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

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

# Show story preview
if st.session_state["story"]:
    story_lines = st.session_state["story"].split("\n")
    title = story_lines[0].strip()
    body_lines = story_lines[1:]

    # Dynamic height for story box
    story_height = min(800, 30 * len(body_lines))  # 30px per line approx

    story_html = f"<div style='text-align:center; font-weight:bold; font-size:18px; margin-bottom:10px;'>{title}</div>"
    story_html += "<br>".join(body_lines)

    st.markdown(
        f"<div class='story-box' style='height:{story_height}px;'>{story_html}</div>",
        unsafe_allow_html=True
    )

    # ======== Download TXT ========
    st.download_button(
        "Download Story (TXT)",
        data=st.session_state["story"].encode("utf-8"),
        file_name="story.txt",
        mime="text/plain",
        key="download-txt-btn"
    )

    # ======== Download PDF ========
    def generate_pdf(text):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story_lines = text.split("\n")
        elements = []

        # Title as bold, centered
        title = story_lines[0].strip()
        elements.append(Paragraph(f"<b><para align=center>{title}</para></b>", styles['Title']))
        elements.append(Spacer(1, 12))

        # Body
        for line in story_lines[1:]:
            if line.strip() != "":
                elements.append(Paragraph(line, styles['Normal']))
                elements.append(Spacer(1, 6))
        doc.build(elements)
        buffer.seek(0)
        return buffer

    pdf_bytes = generate_pdf(st.session_state["story"])
    st.download_button(
        "Download Story (PDF)",
        data=pdf_bytes,
        file_name="story.pdf",
        mime="application/pdf",
        key="download-pdf-btn"
    )
