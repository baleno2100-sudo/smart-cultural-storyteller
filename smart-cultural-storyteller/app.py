import streamlit as st
import sqlite3
import datetime

# ================= CONFIG =================
accent_color = "#FFA500"

# SQLite connection (thread-safe for Streamlit)
conn = sqlite3.connect("stories.db", check_same_thread=False)
c = conn.cursor()

# ================= SESSION STATE =================
if "story" not in st.session_state:
    st.session_state["story"] = ""
if "story_title" not in st.session_state:
    st.session_state["story_title"] = ""
if "moral" not in st.session_state:
    st.session_state["moral"] = ""
if "theme" not in st.session_state:
    st.session_state["theme"] = "dark"
if "show_story" not in st.session_state:
    st.session_state["show_story"] = True

# ================= THEME TOGGLE =================
st.sidebar.title("Theme")
if st.sidebar.button("Toggle Theme"):
    st.session_state["theme"] = "light" if st.session_state["theme"] == "dark" else "dark"

# ================= STORY GENERATION =================
if st.button("Generate Story"):
    # Example story; replace with your generation logic
    st.session_state["story_title"] = "The Brave Soldier and the Whispering Woods"
    st.session_state["story"] = (
        "Once upon a time, in a faraway kingdom, there lived a brave soldier..."
    )
    st.session_state["moral"] = "Courage and kindness always prevail."
    st.session_state["show_story"] = True

# ================= DISPLAY STORY =================
if st.session_state["show_story"] and st.session_state["story"]:
    story_lines = st.session_state["story"].split("\n")
    story_height = min(800, max(400, 30 * len(story_lines)))

    st.markdown(
        f"""
        <style>
        .story-box {{
            position: relative;
            overflow-y: auto;
            padding: 12px 35px 12px 12px;
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
        <div class='story-box'>
            <form action="" method="post">
                <button name="close_story" class='close-btn'>✖</button>
            </form>
            <h2 style='text-align:center; color:{accent_color}; font-size:20px; margin-bottom:6px;'>
                {st.session_state['story_title']}
            </h2>
            {st.session_state['story'].replace('\n', '<br>')}
            <p style='font-weight:bold; color:{accent_color}; margin-top:12px;'>
                Moral: {st.session_state['moral']}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Close story using session state
    if st.button("✖", key="close_story_btn"):
        st.session_state["show_story"] = False

# ================= OPTIONAL: SHOW RESTORED STORY BUTTON =================
if not st.session_state["show_story"] and st.session_state["story"]:
    if st.button("Show Story Again"):
        st.session_state["show_story"] = True
