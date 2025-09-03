import streamlit as st
from datetime import datetime

# --- Page Config ---
st.set_page_config(
    page_title="Smart Cultural Storyteller",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Dark Theme + Scrollbars + Animations ---
st.markdown("""
    <style>
    body {
        font-family: 'Inter', sans-serif;
        background-color: #111827;
        color: #e5e7eb;
    }
    .sidebar .sidebar-content {
        background-color: #1f2937;
    }
    .css-1d391kg { background-color: #111827; }
    .css-1vq4p4l, .stTextInput > div > div > input {
        background-color: #374151;
        color: #f9fafb;
        border-radius: 12px;
        padding: 12px;
    }
    .category-card {
        background: #1f2937;
        border: 2px solid transparent;
        border-radius: 16px;
        padding: 16px;
        text-align: center;
        cursor: pointer;
        transition: transform 0.2s ease;
    }
    .category-card:hover {
        transform: scale(1.05);
        border-color: #facc15;
    }
    .story-container {
        background: #374151;
        padding: 20px;
        border-radius: 16px;
        max-height: 300px;
        overflow-y: auto;
    }
    .story-container::-webkit-scrollbar {
        width: 8px;
    }
    .story-container::-webkit-scrollbar-thumb {
        background: #4a5568;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar Navigation ---
st.sidebar.markdown("### 📚 Cultural Storyteller")
menu = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard", "✨ Storyteller", "🌍 Cultures", "📖 My Stories", "⚙️ Settings"]
)

# --- Main Header ---
st.markdown("#### Welcome to Cultural Storyteller")
st.markdown("<h1 style='color:white;'>Discover stories from around the world</h1>", unsafe_allow_html=True)

# --- Categories ---
st.markdown("## Choose a Category")
cols = st.columns(6)
categories = {
    "Folk Tales": "📜",
    "History": "🏛️",
    "Traditions": "🎨",
    "Mythology": "⚡",
    "Heroes": "🦸‍♂️",
    "Festivals": "🎉"
}

selected_category = None
for i, (cat, icon) in enumerate(categories.items()):
    with cols[i]:
        if st.button(f"{icon}\n{cat}", key=cat):
            selected_category = cat

if not selected_category:
    selected_category = "Folk Tales"

# --- Story Generator ---
st.markdown("## Create Your Story")
topic = st.text_input("Describe the story you'd like to hear:", 
                      placeholder="e.g. Tell me about the legend of King Arthur from Celtic tradition")

st.markdown(f"**Category:** {selected_category}")

generate = st.button("✨ Generate Story")

if generate and topic:
    # Placeholder story (replace with Gemini/Firebase API calls)
    story_title = f"The Legend of {topic.title()}"
    story_body = "Once upon a time in a faraway land, there lived a hero..."
    story_moral = "Moral: Courage and kindness always win."

    # --- Story Content Display ---
    st.image("https://placehold.co/800x450/1a202c/e2e8f0?text=Story+Image", use_column_width=True)
    st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")

    st.markdown(f"### {story_title}")
    st.markdown(f"<div class='story-container'>{story_body}</div>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#facc15;'><i>{story_moral}</i></p>", unsafe_allow_html=True)

    # Download buttons
    st.download_button("📥 Download Story as PDF", data=story_body, file_name="story.pdf")
    st.download_button("📥 Download Image", data="fake_image_bytes", file_name="story.png")

# --- Featured Stories ---
st.markdown("## Featured Stories")
featured = [
    {"title": "The Monkey King", "body": "A tale of wisdom and mischief from Chinese folklore."},
    {"title": "Rama’s Return", "body": "An episode from the Ramayana celebrating the triumph of good."}
]

cols = st.columns(3)
for i, story in enumerate(featured):
    with cols[i % 3]:
        st.markdown(f"### {story['title']}")
        st.markdown(story['body'][:100] + "...")
