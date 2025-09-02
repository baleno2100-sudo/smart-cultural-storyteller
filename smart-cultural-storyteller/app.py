import streamlit as st
import sqlite3
import datetime

# ================= CONFIG =================
accent_color = "#FFA500"  # Orange for cross & accents
DB_NAME = "stories.db"

# ================= THEME =================
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme=="dark" else "dark"

# ================= SESSION STATE =================
if "show_story" not in st.session_state:
    st.session_state.show_story = True

if "story" not in st.session_state:
    st.session_state.story = "Once upon a time, in a faraway kingdom..."
    st.session_state.story_title = "The Brave Soldier and the Whispering Woods"
    st.session_state.moral = "Courage and kindness always win."

# ================= DATABASE =================
conn = sqlite3.connect(DB_NAME, check_same_thread=False)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS stories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    story TEXT,
    moral TEXT,
    category TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# ================= LAYOUT =================
st.set_page_config(page_title="Story App", page_icon="📖", layout="wide")
st.title("📖 Story Teller")

# Theme toggle button
st.button("Toggle Theme 🌞/🌙", on_click=toggle_theme)

# ================= STORY BOX =================
if st.session_state.show_story:
    story_lines = st.session_state["story"].split("\n")
    story_height = min(800, max(400, 30 * len(story_lines)))

    story_html = f"""
    <div class='story-box'>
        <button class='close-btn' onclick="window.parent.postMessage({{'type':'close_story'}}, '*')">✖</button>
        <h2 style='text-align:center; color:{accent_color}; font-size:20px; margin-bottom:6px;'>
            {st.session_state.get('story_title', '')}
        </h2>
        {st.session_state['story'].replace('\n', '<br>')}
        <p style='font-weight:bold; color:{accent_color}; margin-top:12px;'>
            Moral: {st.session_state.get('moral', '')}
        </p>
    </div>

    <style>
        .story-box {{
            position: relative;
            overflow-y: auto;
            padding: 12px 35px 12px 12px;  /* space for cross */
            background-color: {'#1e1e1e' if st.session_state['theme']=='dark' else '#f9f9f9'};
            border: 1px solid {accent_color};
            border-radius: 10px;
            color: {'#FFFFFF' if st.session_state['theme']=='dark' else '#000000'};
            scrollbar-width: thin; 
            scrollbar-color: {'#888 #333' if st.session_state['theme']=='dark' else '#555 #DDD'};
            scroll-behavior: smooth;
            margin-bottom:10px;
            max-height:{story_height}px;
        }}
        .close-btn {{
            position: absolute;
            top: 5px;
            right: 10px;
            background: transparent;
            border: none;
            font-size: 18px;
            font-weight: bold;
            color: {accent_color};
            cursor: pointer;
        }}
        .close-btn:hover {{
            color: darkorange;
        }}
    </style>
    """
    st.markdown(story_html, unsafe_allow_html=True)

# ================= HANDLE CLOSE BUTTON =================
st.write(
    "<script>"
    "window.addEventListener('message', (event) => {"
    " if(event.data.type === 'close_story'){"
    "   const story = document.querySelector('.story-box');"
    "   if(story){ story.style.display='none'; }"
    "   window.parent.postMessage({type:'story_closed'}, '*');"
    "}"
    "});"
    "</script>",
    unsafe_allow_html=True
)

# Restore story button if minimized
if not st.session_state.show_story:
    if st.button("Show Story Again"):
        st.session_state.show_story = True

# ================= FEATURED STORIES GRID (EXAMPLE) =================
featured_stories = [
    {"title":"The Lost Dragon","id":1},
    {"title":"The Clever Fox","id":2},
    {"title":"The Magic Tree","id":3},
    {"title":"The Brave Knight","id":4},
]

st.subheader("Featured Stories")
cols = st.columns(2)
for idx, story in enumerate(featured_stories):
    with cols[idx % 2]:
        st.markdown(f"""
        <div class='story-card'>
            <h4>{story['title']}</h4>
        </div>
        <style>
        .story-card {{
            padding:10px;
            background-color: {'#2e2e2e' if st.session_state['theme']=='dark' else '#EEE'};
            color: {'#FFF' if st.session_state['theme']=='dark' else '#000'};
            border-radius:10px;
            margin-bottom:10px;
        }}
        </style>
        """, unsafe_allow_html=True)
