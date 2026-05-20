from html import escape
import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Backend.Functions.post_handler import (
    update_post,
    get_post_by_id
)
from Backend.Functions.library_data import (
    get_reader_from_session,
    reader_initials,
    get_book_by_isbn,
    get_books_by_title,
)

from components.ui_helpers import (
    COLORS,
    inject_global_css,
    page_spacer,
    render_avatar,
    render_login_required,
    render_navbar,
    section_title,
)

# ---------------- PAGE SETUP ----------------
st.set_page_config(
    page_title="Edit_Post",
    page_icon="LT",
    layout="wide",
)

inject_global_css()
render_navbar(active_page="my_library")
page_spacer(30)

# ---------------- AUTH ----------------
current_reader = get_reader_from_session(st.session_state)
if current_reader is None:
    render_login_required("Please sign in before editing a post.")
    st.stop()

# ---------------- LOAD POST ----------------
post_id = st.session_state.get("edit_post_id")

if not post_id:
    st.error("No post selected for editing.")
    st.stop()

post = get_post_by_id(post_id)[0]

if not post:
    st.error("Post not found.")
    st.stop()

# ---------------- UI ----------------
_, center_col, _ = st.columns([1, 2.5, 1])

with center_col:
    section_title("Edit your post")

    st.markdown(
        f'<div style="display:flex; align-items:center; gap:12px; margin-bottom:20px;">'
        f'{render_avatar(reader_initials(current_reader["Name"]), COLORS["gold"], COLORS["brown"], "normal")}'
        f'<strong style="font-size:1rem; color:{COLORS["dark_green"]};">{escape(current_reader["Name"])}</strong>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ---------------- PREFILL CONTENT ----------------
    post_content = st.text_area(
        "What is on your mind?",
        value=post.get("Content", ""),
        height=160,
        key="edit_post_content",
        label_visibility="collapsed",
    )

    page_spacer(8)

    # ---------------- BOOK LINK (PRESELECT) ----------------
    search_type = st.radio("Search by", ["Title", "ISBN"], horizontal=True)

    keyword = ""
    books = []

    if search_type == "Title":
        keyword = st.text_input("Enter book title")
        books = get_books_by_title(keyword) if keyword else []
    else:
        isbn = st.text_input("Enter ISBN")
        books = get_book_by_isbn(isbn) if isbn else []

    # normalize single-book response
    if isinstance(books, dict):
        books = [books]

    book_options = {"No book linked": None}

    for b in books:
        book_options[f'{b["Title"]} - {b["Author"]}'] = b["ISBN"]

    # preselect current linked book (if exists)
    current_isbn = post.get("ISBN")
    current_post_id = post.get("Post_ID")
    default_label = "No book linked"

    for label, isbn_val in book_options.items():
        if isbn_val == current_isbn:
            default_label = label
            break

    linked_book = st.selectbox(
        "Select book",
        list(book_options.keys()),
        index=list(book_options.keys()).index(default_label),
    )

    page_spacer(12)

    # ---------------- ACTIONS ----------------
    publish_col, cancel_col = st.columns([3, 1])

    with publish_col:
        if st.button("Update post", type="primary", use_container_width=True):

            if not post_content.strip():
                st.error("Post content cannot be empty.")
                st.stop()

            success, message = update_post(
                post_id=post_id,
                content=post_content,
                isbn=book_options[linked_book]
            )

            if success:
                st.success("Your post has been updated successfully.")
            else:
                st.error(message)