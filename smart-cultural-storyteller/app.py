import streamlit as st
import requests
import io
import datetime
import sqlite3
import base64
from PIL import Image
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from openai import OpenAI

# ================= CONFIG =================
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
MODEL = "google/gemini-2.5-flash-image-preview"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
accent_color = "#FFA500"
# ===========================================

# ======== Page Setup ========
st.set_page_config(page_title="Smart Cultural Storyteller", page_icon="🎭", layout="centered")

# ======== Theme ========
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
    st.markdown(
        f"""
        <style>
            .stApp {{background-color: {'#222222' if st.session_state['theme']=='dark' else '#f9f9f9'}; 
                   color: {'#FFFFFF' if st.session_state['theme']=='dark' else '#000000'};}}
            .stButton button {{
                background-color: {accent_color};
                color: white;
                font-weight: bold;
                border-radius: 10px;
            }}
            .story-box {{
                overflow-y: auto;
                padding: 12px;
                border: 1px solid {accent_color};
                border-radius: 10px;
                scrollbar-width: thin;
                scrollbar-color: {'#888 #333' if st.session_state['theme']=='dark' else '#555 #DDD'};
                max-height: 400px;
                margin-bottom:10px;
            }}
        </style>
        """,
        unsafe_allow_html=True
    )

apply_theme()

# ======== SQLite DB ========
conn = sqlite3.connect("stories.db", check_same_thread=False)
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS stories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            story TEXT,
            moral TEXT,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)""")
conn.commit()

# ======== Story Generation ========
def generate_story(prompt, category, max_tokens=800):
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    story_type = {
        "Folk Tale": "You are a magical storyteller. Retell folk tales in a vivid, enchanting way. Minimum 500 words.",
        "Historical Event": "You are a historian. Retell historical events engagingly with characters and context.",
        "Tradition": "You are a cultural guide. Explain traditions with stories in a captivating way."
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": story_type.get(category, story_type["Folk Tale"])},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.8
    }
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 402:
            return "⚠️ API credit limit reached. Reduce max_tokens or recharge account."
        elif response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Exception occurred: {str(e)}"

def generate_story_with_title(prompt, category):
    full_prompt = (
        f"{prompt}\n\nAlso provide:\n"
        "1. A short, catchy title for this story.\n"
        "2. The moral of the story in one sentence.\n"
        "Return in format:\n"
        "TITLE: <title>\nSTORY:\n<story text>\nMORAL: <moral text>"
    )
    response_text = generate_story(full_prompt, category)
    title, story, moral = "Untitled", "", ""
    try:
        title = response_text.split("TITLE:")[1].split("STORY:")[0].strip()
        story = response_text.split("STORY:")[1].split("MORAL:")[0].strip()
        moral = response_text.split("MORAL:")[1].strip()
    except Exception:
        story = response_text
    return title, story, moral

# ======== Image Generation ========
def generate_image(prompt):
    try:
        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[{"role":"user","content":[{"type":"text","text":prompt}]}],
            modalities=["image"]
        )
        img_b64 = completion.choices[0].message.content[0]["image"]["b64_json"]
        return Image.open(io.BytesIO(base64.b64decode(img_b64)))
    except Exception as e:
        return None

# ======== PDF Export ========
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
    title_style = ParagraphStyle("TitleStyle", parent=styles["Heading1"], fontName="Helvetica-Bold",
                                 fontSize=20, textColor=colors.HexColor(accent_color), alignment=1, spaceAfter=6)
    body_style = ParagraphStyle("BodyStyle", parent=styles["Normal"], fontName="Helvetica", fontSize=12,
                                leading=16, textColor=colors.black)
    moral_style = ParagraphStyle("MoralStyle", parent=styles["Normal"], fontName="Helvetica-Bold",
                                 fontSize=12, leading=16, textColor=colors.HexColor(accent_color), spaceBefore=12)

    if "\n\nMoral:" in story_text:
        parts = story_text.split("\n\nMoral:")
        story_body = parts[0]
        moral = parts[1].strip()
    else:
        story_body = story_text
        moral = ""

    story_elements = [Paragraph(story_body.split("\n")[0], title_style), Spacer(1,6)]
    for line in story_body.split("\n")[1:]:
        if line.strip():
            story_elements.append(Paragraph(line.strip(), body_style))
            story_elements.append(Spacer(1,4))
    if moral:
        story_elements.append(Paragraph("Moral: " + moral, moral_style))

    doc.build(story_elements, onFirstPage=add_footer, onLaterPages=add_footer)
    buffer.seek(0)
    return buffer

# ======== UI ========
st.title("🎭 Smart Cultural Storyteller")
st.markdown("Retell **Folk Tales**, **Historical Events**, and **Traditions** with AI magic ✨")

# Sidebar Category
st.sidebar.header("Choose a Category")
category = st.sidebar.radio(
    "Pick one:",
    ["Folk Tale", "Historical Event", "Tradition"],
    format_func=lambda x: f"🌟 {x}" if x=="Folk Tale" else ("📜 "+x if x=="Historical Event" else "🎎 "+x)
)

# ======== Session State ========
for key in ["story", "story_title", "moral", "prompt", "expanded_stories", "story_image"]:
    if key not in st.session_state:
        st.session_state[key] = {} if key=="expanded_stories" else ""

# ======== Story Generation Trigger ========
def trigger_story_generation():
    if not st.session_state["prompt"].strip():
        st.warning("⚠️ Please enter a prompt first!")
    else:
        with st.spinner("Generating story & image... 🌌"):
            title, story, moral = generate_story_with_title(st.session_state["prompt"], category)
            st.session_state["story_title"] = title
            st.session_state["story"] = story
            st.session_state["moral"] = moral

            # Save to DB
            c.execute("INSERT INTO stories (title, story, moral, category) VALUES (?,?,?,?)",
                      (title, story, moral, category))
            conn.commit()

            # Generate image
            img = generate_image(st.session_state["prompt"])
            st.session_state["story_image"] = img

# ======== Prompt Input ========
st.text_input("Enter a prompt to begin your story:", key="prompt", on_change=trigger_story_generation)
if st.button("Generate Story"):
    trigger_story_generation()

# ======== Display Story + Image ========
if st.session_state["story"]:
    st.markdown("<div class='story-box'>", unsafe_allow_html=True)
    st.markdown(f"### {st.session_state['story_title']}", unsafe_allow_html=True)
    st.write(st.session_state["story"])
    st.markdown(f"**Moral:** {st.session_state['moral']}")
    st.markdown("</div>", unsafe_allow_html=True)

    # Image display & download
    if st.session_state["story_image"]:
        st.image(st.session_state["story_image"], caption="AI Generated Illustration")
        img_buffer = io.BytesIO()
        st.session_state["story_image"].save(img_buffer, format="PNG")
        st.download_button("📥 Download Image", data=img_buffer.getvalue(), file_name=f"{st.session_state['story_title']}.png", mime="image/png")

    # TXT download
    full_text = f"{st.session_state['story_title']}\n\n{st.session_state['story']}\n\nMoral: {st.session_state['moral']}"
    st.download_button("📥 Download as TXT", data=full_text.encode("utf-8"), file_name=f"{st.session_state['story_title']}.txt", mime="text/plain")
    
    # PDF download
    pdf_buffer = create_pdf(full_text)
    st.download_button("📥 Download as PDF", data=pdf_buffer, file_name=f"{st.session_state['story_title']}.pdf", mime="application/pdf")

# ======== Featured Stories Grid ========
st.subheader("🌟 Featured Stories")
c.execute("SELECT id, title FROM stories ORDER BY created_at DESC LIMIT 20")
stories = c.fetchall()

columns_per_row = 2
rows = [stories[i:i+columns_per_row] for i in range(0, len(stories), columns_per_row)]

for row_stories in rows:
    cols = st.columns(columns_per_row)
    for idx, s in enumerate(row_stories):
        story_id, title = s
        if story_id not in st.session_state["expanded_stories"]:
            st.session_state["expanded_stories"][story_id] = False

        with cols[idx]:
            clicked = st.button(title, key=f"story_{story_id}")
            if clicked:
                st.session_state["expanded_stories"][story_id] = not st.session_state["expanded_stories"][story_id]

            if st.session_state["expanded_stories"][story_id]:
                c.execute("SELECT story, moral FROM stories WHERE id=?", (story_id,))
                row_data = c.fetchone()
                if row_data:
                    story_text, moral_text = row_data
                    st.markdown(f"<div class='story-box'><b>{title}</b><br>{story_text}<br><b>Moral:</b> {moral_text}</div>", unsafe_allow_html=True)
                    full_text_card = f"{title}\n\n{story_text}\n\nMoral: {moral_text}"
                    pdf_buffer_card = create_pdf(full_text_card)
                    st.download_button("📥 Download PDF", data=pdf_buffer_card, file_name=f"{title}.pdf", mime="application/pdf")
