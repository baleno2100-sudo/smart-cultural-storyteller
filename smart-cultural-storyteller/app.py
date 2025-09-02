import streamlit as st

# ================= Page Config =================
st.set_page_config(page_title="Smart Cultural Storyteller", page_icon="✨", layout="centered")

# ================= Title =================
st.title("✨ Smart Cultural Storyteller")

# ================= Story Input =================
user_input = st.text_area("Enter a theme or prompt for your story:")

# ================= Theme Toggle =================
if "story_theme" not in st.session_state:
    st.session_state["story_theme"] = "dark"

col1, col2 = st.sidebar.columns([1, 1])
with col1:
    if st.button("🌙 Dark", disabled=(st.session_state["story_theme"] == "dark")):
        st.session_state["story_theme"] = "dark"
with col2:
    if st.button("☀️ Light", disabled=(st.session_state["story_theme"] == "light")):
        st.session_state["story_theme"] = "light"

# ================= Generate Story =================
if st.button("Generate Story"):
    if user_input.strip():
        # Simulate AI story generation (replace with actual OpenAI call if needed)
        st.session_state["story"] = f"Here is your story based on: **{user_input}**. \n\nOnce upon a time..."
    else:
        st.warning("⚠️ Please enter a theme or prompt before generating a story.")

# ================= Story Box Styling =================
if "story" in st.session_state and st.session_state["story"]:
    if st.session_state["story_theme"] == "dark":
        story_bg = "#1e1e1e"
        story_text = "#FFFFFF"
        scrollbar = "#888888"
    else:
        story_bg = "#FFFFFF"
        story_text = "#000000"
        scrollbar = "#222222"

    st.subheader("📖 Your Story:")
    st.markdown(
        f"""
        <style>
            .story-box {{
                background-color: {story_bg};
                color: {story_text};
                padding: 15px;
                border-radius: 12px;
                max-height: 400px;
                overflow-y: auto;
                border: 1px solid #666;
                font-size: 16px;
                line-height: 1.5;
            }}
            .story-box::-webkit-scrollbar {{
                width: 8px;
            }}
            .story-box::-webkit-scrollbar-thumb {{
                background-color: {scrollbar};
                border-radius: 10px;
            }}
        </style>
        <div class="story-box">{st.session_state['story']}</div>
        """,
        unsafe_allow_html=True
    )

    # Download option
    st.download_button(
        "Download Story",
        data=st.session_state["story"].encode("utf-8"),
        file_name="story.txt",
        mime="text/plain"
    )
