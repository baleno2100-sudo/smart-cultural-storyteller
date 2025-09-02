import streamlit as st
import requests
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# ================= CONFIG =================
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
MODEL = "openai/gpt-4o-mini"

# ================= SESSION STATE =================
if "story" not in st.session_state:
    st.session_state["story"] = ""
if "story_title" not in st.session_state:
    st.session_state["story_title"] = ""
if "moral" not in st.session_state:
    st.session_state["moral"] = ""
if "expanded_stories" not in st.session_state:
    st.session_state["expanded_stories"] = {}

# Accent color
accent_color = "#FFA500"  # Orange

# ================= CSS =================
st.markdown(f"""
<style>
    .story-box {{
        position: relative;
        padding: 12px 16px;
        border: 1px solid {accent_color};
        border-radius: 10px;
        background-color: {'#1e1e1e' if st.session_state.get('theme', 'dark')=='dark' else '#f9f9f9'};
        color: {'#FFFFFF' if st.session_state.get('theme', 'dark')=='dark' else '#000000'};
        margin-bottom:10px;
    }}
    .story-title {{
        text-align:center;
        font-weight:bold;
        color:{accent_color};
        font-size:20px;
        margin-bottom:6px;
    }}
    .moral-text {{
        font-weight:bold;
        color:{accent_color};
        margin-top:12px;
    }}
</style>
""", unsafe_allow_html=True)

# ================= PDF CREATION =================
def create_pdf(text):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story_flow = []
    for line in text.split("\n"):
        story_flow.append(Paragraph(line, styles["Normal"]))
        story_flow.append(Spacer(1, 6))
    doc.build(story_flow)
    buffer.seek(0)
    return buffer

# ================= INPUT =================
st.title("Story Generator")
prompt = st.text_area("Enter your story prompt here:")

if st.button("Generate Story"):
    # Dummy story generation for example
    st.session_state["story_title"] = "The Brave Soldier and the Whispering Woods"
    st.session_state["story"] = "Once upon a time, there was a brave soldier who ventured into the mysterious woods..."
    st.session_state["moral"] = "Courage and wisdom go hand in hand."

# ================= DISPLAY GENERATED STORY =================
if st.session_state["story"]:
    gen_story_id = "generated"
    if gen_story_id not in st.session_state["expanded_stories"]:
        st.session_state["expanded_stories"][gen_story_id] = True

    with st.container():
        # Title + close button row
        cols = st.columns([0.9, 0.1])
        with cols[0]:
            st.markdown(
                f"<p class='story-title'>{st.session_state['story_title']}</p>",
                unsafe_allow_html=True
            )
        with cols[1]:
            if st.button("✖", key="close_generated"):
                st.session_state["story"] = ""
                st.session_state["story_title"] = ""
                st.session_state["moral"] = ""
                st.session_state["expanded_stories"].pop(gen_story_id, None)

        # Story content
        if st.session_state["expanded_stories"].get(gen_story_id, True):
            st.markdown(
                f"<div class='story-box'>{st.session_state['story'].replace(chr(10), '<br>')}<br><span class='moral-text'>Moral: {st.session_state['moral']}</span></div>",
                unsafe_allow_html=True
            )

        # Download buttons
        full_text = f"{st.session_state['story_title']}\n\n{st.session_state['story']}\n\nMoral: {st.session_state['moral']}"
        pdf_buffer = create_pdf(full_text)
        d_col1, d_col2 = st.columns(2)
        with d_col1:
            st.download_button(
                label="📥 Download TXT",
                data=full_text.encode("utf-8"),
                file_name=f"{st.session_state['story_title']}.txt",
                mime="text/plain",
                key="download_txt_generated"
            )
        with d_col2:
            st.download_button(
                label="📥 Download PDF",
                data=pdf_buffer,
                file_name=f"{st.session_state['story_title']}.pdf",
                mime="application/pdf",
                key="download_pdf_generated"
            )
