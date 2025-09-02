import streamlit as st
import sqlite3
import datetime

# ======== CONFIG ========
accent_color = "#FFA500"

# ======== DATABASE SETUP ========
conn = sqlite3.connect("stories.db", check_same_thread=False)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS stories(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    category TEXT,
    story TEXT,
    moral TEXT,
    prompt TEXT,
    created_at TEXT
)
""")
conn.commit()

# ======== SESSION STATE ========
if "expanded_stories" not in st.session_state:
    st.session_state["expanded_stories"] = {}
if "theme" not in st.session_state:
    st.session_state["theme"] = "light"

# ======== UTILITY FUNCTIONS ========
def clean_title(title):
    return title.replace("**", "").strip()

def save_story(title, category, story, moral, prompt):
    c.execute("INSERT INTO stories (title, category, story, moral, prompt, created_at) VALUES (?, ?, ?, ?, ?, ?)",
              (title, category, story, moral, prompt, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()

def get_all_stories(limit=20):
    c.execute("SELECT id, title FROM stories ORDER BY created_at DESC LIMIT ?", (limit,))
    return c.fetchall()

def get_story_by_id(story_id):
    c.execute("SELECT story, moral FROM stories WHERE id=?", (story_id,))
    return c.fetchone()

# ======== PAGE NAVIGATION ========
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to:", ["Generate Story", "Featured Stories"])

# ======== GENERATE STORY PAGE ========
if page == "Generate Story":
    st.title("🎭 Smart Cultural Storyteller")
    st.markdown("Retell **Folk Tales**, **Historical Events**, and **Traditions** with AI magic ✨")

    category = st.selectbox(
        "Select Story Category:",
        ["Folk Tale", "Historical Event", "Tradition"]
    )

    prompt = st.text_input("Enter a prompt to begin your story:")

    if st.button("Generate Story") and prompt:
        # For demo, generate dummy story
        generated_title = f"{prompt.split()[0].title()} Adventure"
        generated_story = f"This is a story based on the prompt: {prompt}.\nIt is a captivating tale!"
        generated_moral = "Always be brave and kind."
        save_story(generated_title, category, generated_story, generated_moral, prompt)

        st.markdown(f"<h2 style='color:{accent_color}; font-weight:bold;'>{clean_title(generated_title)}</h2>", unsafe_allow_html=True)
        st.markdown(f"<div>{generated_story.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-weight:bold; color:{accent_color}; margin-top:12px;'>Moral: {generated_moral}</p>", unsafe_allow_html=True)

# ======== FEATURED STORIES PAGE ========
else:
    st.subheader("🌟 Featured Stories")
    stories = get_all_stories(limit=20)

    # CSS for grid layout
    st.markdown(f"""
    <style>
    .story-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 15px;
    }}
    .story-card {{
        background-color: {'#1e1e1e' if st.session_state['theme']=='dark' else '#f9f9f9'};
        color: {'#FFF' if st.session_state['theme']=='dark' else '#000'};
        border: 2px solid {accent_color};
        border-radius: 10px;
        padding: 12px;
        cursor: pointer;
        transition: transform 0.2s, box-shadow 0.2s;
    }}
    .story-card:hover {{
        transform: scale(1.03);
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }}
    .story-card-title {{
        font-weight: bold;
        color: {accent_color};
        font-size: 18px;
    }}
    .story-box {{
        border: 1px solid {accent_color};
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 15px;
    }}
    </style>
    <div class='story-grid'>
    """, unsafe_allow_html=True)

    for s in stories:
        story_id, title = s
        if story_id not in st.session_state["expanded_stories"]:
            st.session_state["expanded_stories"][story_id] = False

        # Clicking card toggles expanded state
        if st.button(clean_title(title), key=f"story_{story_id}"):
            st.session_state["expanded_stories"][story_id] = not st.session_state["expanded_stories"][story_id]

        st.markdown(f"""
        <div class='story-card'>
            <div class='story-card-title'>{clean_title(title)}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Render expanded stories below grid
    for s in stories:
        story_id, title = s
        if st.session_state["expanded_stories"][story_id]:
            story_data = get_story_by_id(story_id)
            if story_data:
                story_text, moral_text = story_data
                st.markdown(f"""
                <div class='story-box'>
                    <p style='font-weight:bold; color:{accent_color};'>{clean_title(title)}</p>
                    {story_text.replace(chr(10), '<br>')}
                    <p style='font-weight:bold; color:{accent_color}; margin-top:12px;'>Moral: {moral_text}</p>
                </div>
                """, unsafe_allow_html=True)
