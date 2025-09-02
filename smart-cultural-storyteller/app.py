# ======== Display Generated Story as Card (Minimizable) ========
if st.session_state["story"]:
    story_id = "generated"  # Unique key for the generated story
    if story_id not in st.session_state:
        st.session_state[story_id] = True  # True = expanded

    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        st.markdown(f"### {st.session_state.get('story_title','')}")
    with col2:
        if st.button("➖" if st.session_state[story_id] else "➕", key=f"toggle_{story_id}"):
            st.session_state[story_id] = not st.session_state[story_id]

    if st.session_state[story_id]:  # Show story content if expanded
        story_text = st.session_state["story"]
        moral_text = st.session_state.get("moral", "")
        story_card_html = f"""
        <div class='story-card'>
            {story_text.replace('\n','<br>')}
            <p style='font-weight:bold; color:{accent_color}; margin-top:12px;'>Moral: {moral_text}</p>
        </div>
        <style>
            .story-card {{
                overflow-y: auto;
                padding: 12px;
                background-color: {'#1e1e1e' if st.session_state['theme']=='dark' else '#f9f9f9'};
                border: 1px solid {accent_color};
                border-radius: 10px;
                color: {'#FFFFFF' if st.session_state['theme']=='dark' else '#000000'};
                scrollbar-width: thin;
                scrollbar-color: {'#888 #333' if st.session_state['theme']=='dark' else '#555 #DDD'};
                scroll-behavior: smooth;
                margin-bottom:10px;
                max-height:400px;
            }}
        </style>
        """
        st.markdown(story_card_html, unsafe_allow_html=True)

        full_text = f"{st.session_state.get('story_title','')}\n\n{story_text}\n\nMoral: {moral_text}"
        pdf_buffer = create_pdf(full_text)

        col1, col2 = st.columns(2)
        with col1:
            st.download_button("📥 Download TXT", data=full_text.encode("utf-8"),
                               file_name=f"{st.session_state.get('story_title','story')}.txt", mime="text/plain")
        with col2:
            st.download_button("📥 Download PDF", data=pdf_buffer,
                               file_name=f"{st.session_state.get('story_title','story')}.pdf", mime="application/pdf")


# ======== Featured Stories in Grid (Minimizable) ========
st.subheader("🌟 Featured Stories")
c.execute("SELECT id, title FROM stories ORDER BY created_at DESC LIMIT 20")
stories = c.fetchall()

columns_per_row = 2
rows = [stories[i:i+columns_per_row] for i in range(0, len(stories), columns_per_row)]

for row_stories in rows:
    cols = st.columns(columns_per_row)
    for idx, s in enumerate(row_stories):
        story_id, title = s
        key_expanded = f"expanded_{story_id}"
        if key_expanded not in st.session_state:
            st.session_state[key_expanded] = False

        with cols[idx]:
            col1, col2 = st.columns([0.85, 0.15])
            with col1:
                st.markdown(f"### {title}")
            with col2:
                if st.button("➖" if st.session_state[key_expanded] else "➕", key=f"toggle_{story_id}"):
                    st.session_state[key_expanded] = not st.session_state[key_expanded]

            if st.session_state[key_expanded]:
                c.execute("SELECT story, moral FROM stories WHERE id=?", (story_id,))
                row_data = c.fetchone()
                if row_data:
                    story_text, moral_text = row_data
                    story_card_html = f"""
                    <div class='story-card'>
                        {story_text.replace('\n','<br>')}
                        <p style='font-weight:bold; color:{accent_color}; margin-top:12px;'>Moral: {moral_text}</p>
                    </div>
                    <style>
                        .story-card {{
                            overflow-y: auto;
                            padding: 12px;
                            background-color: {'#1e1e1e' if st.session_state['theme']=='dark' else '#f9f9f9'};
                            border: 1px solid {accent_color};
                            border-radius: 10px;
                            color: {'#FFFFFF' if st.session_state['theme']=='dark' else '#000000'};
                            scrollbar-width: thin;
                            scrollbar-color: {'#888 #333' if st.session_state['theme']=='dark' else '#555 #DDD'};
                            scroll-behavior: smooth;
                            margin-bottom:10px;
                            max-height:300px;
                        }}
                    </style>
                    """
                    st.markdown(story_card_html, unsafe_allow_html=True)

                    full_text_card = f"{title}\n\n{story_text}\n\nMoral: {moral_text}"
                    pdf_buffer_card = create_pdf(full_text_card)
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button("📥 TXT", data=full_text_card.encode("utf-8"),
                                           file_name=f"{title}.txt", mime="text/plain")
                    with col2:
                        st.download_button("📥 PDF", data=pdf_buffer_card,
                                           file_name=f"{title}.pdf", mime="application/pdf")
