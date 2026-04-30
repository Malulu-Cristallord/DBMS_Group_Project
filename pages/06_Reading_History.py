from html import escape
import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Backend.Functions.library_data import get_posts, get_reader_from_session
from components.ui_helpers import (
    COLORS,
    inject_global_css,
    page_spacer,
    render_badge,
    render_book_cover,
    render_navbar,
    render_stars,
    section_title,
)


st.set_page_config(
    page_title="Reading History | LibTrack",
    page_icon="LT",
    layout="wide",
)

inject_global_css()
render_navbar(active_page="my_library")
page_spacer(20)


current_reader = get_reader_from_session(st.session_state)
if current_reader is None:
    st.warning("Please sign in to view reading history.")
    if st.button("Go to Login", type="primary"):
        st.switch_page("pages/01_Login.py")
    st.stop()


section_title("Reading activity")

if not current_reader.get("Show_Reading_History"):
    st.warning("Reading history is hidden for this reader. You can change this in Settings.")
    st.stop()


reader_posts = get_posts(reader_id=current_reader["Reader_ID"], limit=30)

if not reader_posts:
    st.info("No reading activity has been recorded yet.")

for post in reader_posts:
    col_cover, col_body, col_meta = st.columns([0.6, 4, 1])

    with col_cover:
        st.markdown(render_book_cover(post.get("cover") or COLORS["mid_green"]), unsafe_allow_html=True)

    with col_body:
        st.markdown(
            f'<strong>{escape(post.get("book_title") or "Unlinked book")}</strong><br>'
            f'<span class="secondary">{escape(post.get("author") or "Unknown author")}</span><br>'
            f'<span class="muted">{escape(post.get("content") or "")}</span>',
            unsafe_allow_html=True,
        )

    with col_meta:
        if post.get("rating"):
            st.markdown(render_stars(post["rating"]), unsafe_allow_html=True)
        st.markdown(render_badge(str(post.get("created_at") or "No date"), "beige"), unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
