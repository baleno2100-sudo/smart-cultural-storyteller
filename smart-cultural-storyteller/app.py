import streamlit as st

# --- Page Setup ---
st.set_page_config(
    page_title="Cultural Storyteller",
    layout="wide"
)

# --- Custom CSS ---
st.markdown("""
    <style>
    body {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
        color: #f9fafb;
    }
    .category-card {
        background: #1f2937;
        border-radius: 12px;
        padding: 18px;
        text-align: center;
        border: 2px solid transparent;
        transition: transform 0.2s ease, border-color 0.2s ease, background 0.2s ease;
        cursor: pointer;
        margin-bottom: 12px;
        min-height: 120px;
    }
    .category-card:hover {
        transform: scale(1.05);
        border-color: #facc15;
    }
    .category-card.selected {
        border-color: #facc15;
        background: rgba(250, 204, 21, 0.1);
    }
    .story-box {
        background: #1f2937;
        padding: 20px;
        border-radius: 16px;
        margin-top: 20px;
    }
    .stRadio > div {flex-direction: row;}
    
    /* Golden Button */
    div.stButton > button:first-child {
        background-color: #facc15;
        color: #111827;
        font-weight: bold;
        border-radius: 12px;
        padding: 10px 20px;
        border: none;
        transition: background-color 0.3s ease, transform 0.2s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #eab308;
        transform: scale(1.05);
    }
    </style>
""", unsafe_allow_html=True)

# --- Main Header ---
st.markdown("<h1 style='font-size:2.2em;'>Discover stories from around the world</h1>", unsafe_allow_html=True)

# --- Categories ---
st.markdown("## Choose a Category")
categories = {
    "Folk Tales": "🌸 Traditional stories passed down through generations",
    "History": "🏛️ Historical events and figures brought to life",
    "Traditions": "🎭 Cultural practices and ceremonies",
    "Mythology": "⚡ Ancient myths and legends",
    "Heroes": "🦸 Legendary figures and their adventures",
    "Festivals": "🎉 Cultural celebrations and their origins"
}

if "selected_category" not in st.session_state:
    st.session_state.selected_category = "Folk Tales"

cols = st.columns(6)
for i, (title, desc) in enumerate(categories.items()):
    with cols[i % 6]:
        selected_class = "selected" if st.session_state.selected_category == title else ""
        if st.button(title, key=f"btn_{title}"):
            st.session_state.selected_category = title
        st.markdown(
            f"""
            <div class='category-card {selected_class}'>
                <b>{title}</b><br><small>{desc}</small>
            </div>
            """,
            unsafe_allow_html=True
        )

# --- Story Generator ---
st.markdown("## Create Your Story")

tab_choice = st.radio("Select Format", ["Text", "Audio", "Visual"], horizontal=True)

story_prompt = st.text_input(
    "Describe the story you'd like to hear...",
    placeholder="e.g., Tell me about the legend of King Arthur from Celtic tradition"
)

st.markdown(
    f"<div class='story-box'>Category: <b>{st.session_state.selected_category}</b> | Format: <b>{tab_choice}</b></div>",
    unsafe_allow_html=True
)

if st.button("✨ Generate Story"):
    st.markdown("### 📖 The Legend of King Arthur")
    st.markdown("Once upon a time in a faraway land, there lived a hero...")
    st.markdown("<i>Moral: Courage and kindness always win.</i>", unsafe_allow_html=True)
