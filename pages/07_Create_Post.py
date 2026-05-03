from html import escape
import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Backend.Functions.library_data import (
    create_post,
    get_books,
    get_reader_from_session,
    reader_initials,
    get_book_by_isbn,
    get_books_by_title
)
from components.ui_helpers import (
    COLORS,
    inject_global_css,
    page_spacer,
    render_avatar,
    render_navbar,
    section_title,
)


st.set_page_config(
    page_title="Create Post | LibTrack",
    page_icon="LT",
    layout="wide",
)

inject_global_css()
render_navbar(active_page="my_library")
page_spacer(30)


current_reader = get_reader_from_session(st.session_state)
if current_reader is None:
    st.warning("Please sign in before creating a post.")
    if st.button("Go to Login", type="primary"):
        st.switch_page("pages/01_Login.py")
    st.stop()


_, center_col, _ = st.columns([1, 2.5, 1])

with center_col:
    section_title("Create a post")

    st.markdown(
        f'<div style="display:flex; align-items:center; gap:12px; margin-bottom:20px;">'
        f'{render_avatar(reader_initials(current_reader["Name"]), COLORS["gold"], COLORS["brown"], "normal")}'
        f'<strong style="font-size:1rem; color:{COLORS["dark_green"]};">{escape(current_reader["Name"])}</strong>'
        f'</div>',
        unsafe_allow_html=True,
    )

    post_content = st.text_area(
        "What is on your mind?",
        placeholder="Share your reading thoughts, a quote, a milestone, or a recommendation...",
        height=160,
        key="post_content",
        label_visibility="collapsed",
    )

    page_spacer(8)

    search_type = st.radio("Search by", ["Title", "ISBN"], horizontal=True)

    if search_type == "Title":
        keyword = st.text_input("Enter book title")
        books = get_books_by_title(keyword) if keyword else []
    else:
        isbn = st.text_input("Enter ISBN")
        books = get_book_by_isbn(isbn) if isbn else []

    book_options = {"No book linked": None}
    get_books()
    st.write(books)
    book_options.update({f'{b["Title"]} - {b["Author"]}': b["Book_ID"] for b in books})
    linked_book = st.selectbox("Select book", list(book_options.keys()))
    rating = None
    if book_options[linked_book] is not None:
       rating = st.slider("Rate this book", 1, 5)

    page_spacer(12)

    publish_col, cancel_col = st.columns([3, 1])

    with publish_col:
        if st.button("Publish post", type="primary", use_container_width=True, key="pub_post"):
            success, message = create_post(
                reader_id=current_reader["Reader_ID"],
                book_id=book_options[linked_book],
                content=post_content,
                rating=rating
            )
            if success:
                st.success("Your post has been published to the community feed.")
            else:
                st.error(message)

    with cancel_col:
        if st.button("Cancel", use_container_width=True, key="cancel_post"):
            st.switch_page("app.py")
