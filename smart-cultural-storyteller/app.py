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

# ================= CONFIG =================
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
STORY_MODEL = "openai/gpt-4o-mini"
IMAGE_MODEL = "google/gemini-2.5-flash-image-preview"
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
    bg = "#1e1e1e" if st.session_state["theme"] == "dark" else "#f9f9f9"
    text_color = "#FFFFFF" if st.session_state["theme"] == "dark" else "#000000"
    st.markdown(f"""
        <style>
            .stApp {{background-color: {bg}; color: {text_color};}}
            .stButton button {{
                background-color: {accent_color};
                color: white;
                font-weight: bold;
                border-radius: 10px;
            }}
        </style>
    """, unsafe_allow_html=True)

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

# ======== Session State ========
for key in ["story", "story_title", "moral", "prompt", "expanded_stories", "story_image"]:
    if key not in st.session_state:
        st.session_state[key] = {} if key == "expanded_stories" else ""

# ======== Story Generation ========
def generate_story(prompt, category, max_tokens=600):
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    story_type = {
        "Folk Tale": "You are a magical storyteller. Retell folk tales in a vivid, enchanting way. Minimum 500 words.",
        "Historical Event": "You are a historian. Retell historical events engagingly with characters and context.",
        "Tradition": "You are a cultural guide. Explain traditions with stories in a captivating way."
    }
    payload = {
        "model": STORY_MODEL,
        "messages": [
            {"role": "system", "content": story_type.get(category, story_type["Folk Tale"])},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.8
    }
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        elif response.status_code == 402:
            return "⚠️ API credit limit reached. Reduce max_tokens or upgrade your account."
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {e}"

def generate_story_with_title(prompt, category):
    full_prompt = (
        f"{prompt}\n\nAlso provide:\n"
        "1. A short, catchy title for this story.\n"
        "2. The moral of the story in one sentence.\n"
        "Return the result in this format:\n"
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
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": IMAGE_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt}
                ]
            }
        ],
        "modalities": ["image"]
    }
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            result = response.json()
            images_data = []
            try:
                images_list = result['choices'][0]['message'].get('images', [])
                for img in images_list:
                    img_data = img.get('b64_json', None)
                    if img_data:
                        images_data.append(Image.open(io.BytesIO(base64.b64decode(img_data))))
            except Exception:
                pass
            return images_data
        else:
            return []
    except Exception:
        return []

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

# ======== UI ========
st.title("🎭 Smart Cultural Storyteller")
st.markdown("Retell **Folk Tales**, **Historical Events**, and **Traditions** with AI magic ✨")

# Sidebar Category
st.sidebar.header("Choose a Category")
category = st.sidebar.radio(
    "Pick one:",
    ["Folk Tale", "Historical Event", "Tradition"],
    format_func=lambda x: f"🌟 {x}" if x == "Folk Tale" else ("📜 "+x if x=="Historical Event" else "🎎 "+x)
)

# ======== Story Trigger ========
def trigger_story_generation():
    if not st.session_state["prompt"].strip():
        st.warning("⚠️ Please enter a prompt first!")
        return
    with st.spinner("Summoning your story... 🌌"):
        title, story, moral = generate_story_with_title(st.session_state["prompt"], category)
        st.session_state["story_title"] = title
        st.session_state["story"] = story
        st.session_state["moral"] = moral

        # Generate single image
        images = generate_image(st.session_state["prompt"])
        if images:
            st.session_state["story_image"] = images[0]

        # Save to DB
        c.execute("INSERT INTO stories (title, story, moral, category) VALUES (?,?,?,?)",
                  (title, story, moral, category))
        conn.commit()

st.text_input("Enter a prompt to begin your story:", key="prompt", on_change=trigger_story_generation)
if st.button("Generate Story"):
    trigger_story_generation()

# ======== Display Story + Image ========
if st.session_state["story"]:
    # Scrollable story box
    story_lines = st.session_state["story"].split("\n")
    story_height = min(800, max(400, 30 * len(story_lines)))
    st.markdown(f"<style>.story-box {{height: {story_height}px; overflow-y:auto;}}</style>", unsafe_allow_html=True)

    # Story + image
    st.markdown(f"<div class='story-box' style='border:1px solid {accent_color}; padding:12px; border-radius:10px;'>", unsafe_allow_html=True)
    st.markdown(f"### {st.session_state['story_title']}", unsafe_allow_html=True)
    st.write(st.session_state['story'])
    if st.session_state.get("story_image"):
        st.image(st.session_state["story_image"], use_column_width=True)
    st.markdown(f"**Moral:** {st.session_state['moral']}", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Downloads
    full_text = f"{st.session_state['story_title']}\n\n{st.session_state['story']}\n\nMoral: {st.session_state['moral']}"
    st.download_button("📥 Download TXT", data=full_text.encode("utf-8"), file_name=f"{st.session_state['story_title']}.txt")
    pdf_buffer = create_pdf(full_text)
    st.download_button("📥 Download PDF", data=pdf_buffer, file_name=f"{st.session_state['story_title']}.pdf")
    if st.session_state.get("story_image"):
        img_buf = io.BytesIO()
        st.session_state["story_image"].save(img_buf, format="PNG")
        st.download_button("📥 Download Image", data=img_buf.getvalue(), file_name=f"{st.session_state['story_title']}.png", mime="image/png")

# ======== Featured Stories ========
st.subheader("🌟 Featured Stories")
c.execute("SELECT id, title FROM stories ORDER BY created_at DESC LIMIT 20")
stories = c.fetchall()

cols_per_row = 2
rows = [stories[i:i+cols_per_row] for i in range(0, len(stories), cols_per_row)]
for row_stories in rows:
    cols = st.columns(cols_per_row)
    for idx, (story_id, title) in enumerate(row_stories):
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
                    st.markdown(f"<div class='story-box' style='border:1px solid {accent_color}; padding:12px; border-radius:10px; overflow-y:auto; max-height:400px;'>", unsafe_allow_html=True)
                    st.write(story_text)
                    st.markdown(f"**Moral:** {moral_text}", unsafe_allow_html=True)
                    pdf_buf_card = create_pdf(f"{title}\n\n{story_text}\n\nMoral: {moral_text}")
                    st.download_button("📥 Download PDF", data=pdf_buf_card, file_name=f"{title}.pdf")
                    st.markdown("</div>", unsafe_allow_html=True)
