from html import escape
import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Backend.Functions.library_data import create_post, get_books, get_reader_from_session
from components.ui_helpers import (
    COLORS,
    inject_global_css,
    page_spacer,
    render_book_cover,
    render_navbar,
    section_title,
)


st.set_page_config(
    page_title="Write a Review | LibTrack",
    page_icon="LT",
    layout="wide",
)

inject_global_css()
render_navbar(active_page="my_library")
page_spacer(30)


current_reader = get_reader_from_session(st.session_state)
if current_reader is None:
    st.warning("Please sign in before writing a review.")
    if st.button("Go to Login", type="primary"):
        st.switch_page("pages/01_Login.py")
    st.stop()


books = get_books(sort_option="title")
if not books:
    st.info("No books are available in the database yet.")
    st.stop()


_, center_col, _ = st.columns([0.5, 3, 0.5])

with center_col:
    section_title("Write a review")
    st.markdown(
        '<p class="muted">Share your thoughts with the LibTrack community.</p>',
        unsafe_allow_html=True,
    )
    page_spacer(8)

    default_book_id = st.session_state.get("review_book_id")
    book_options = {f'{book["title"]} - {book["author"]}': book["id"] for book in books}
    option_labels = list(book_options.keys())
    default_index = 0

    if default_book_id:
        for index, label in enumerate(option_labels):
            if str(book_options[label]) == str(default_book_id):
                default_index = index
                break

    selected_label = st.selectbox(
        "Select the book you are reviewing",
        options=option_labels,
        index=default_index,
        key="cr_book_sel",
    )

    selected_book_id = book_options[selected_label]
    selected_book = next(book for book in books if str(book["id"]) == str(selected_book_id))

    mini_col1, mini_col2 = st.columns([0.4, 4])
    with mini_col1:
        st.markdown(render_book_cover(selected_book["cover"]), unsafe_allow_html=True)
    with mini_col2:
        st.markdown(
            f'<strong style="color:{COLORS["dark_green"]};">{escape(selected_book["title"])}</strong><br>'
            f'<span class="muted">{escape(selected_book["author"])} - {escape(selected_book["category"])}</span>',
            unsafe_allow_html=True,
        )

    page_spacer(16)
    st.markdown("<hr>", unsafe_allow_html=True)
    page_spacer(8)

    star_rating = st.select_slider(
        "Your rating",
        options=[1, 2, 3, 4, 5],
        value=4,
        format_func=lambda value: f"{value}/5",
        key="cr_stars",
    )

    page_spacer(8)

    review_title = st.text_input(
        "Review title",
        placeholder="Give your review a short title...",
        key="cr_title",
    )

    review_text = st.text_area(
        "Your review",
        placeholder="What did you think?",
        height=200,
        key="cr_text",
    )

    page_spacer(16)

    submit_col, cancel_col = st.columns([3, 1])

    with submit_col:
        if st.button("Submit review", type="primary", use_container_width=True, key="cr_submit"):
            errors = []
            if not review_title.strip():
                errors.append("Please add a short title to your review.")
            if not review_text.strip():
                errors.append("Please write your review before submitting.")

            if errors:
                for error in errors:
                    st.error(error)
            else:
                content = f"{review_title.strip()}: {review_text.strip()}"
                success, message = create_post(
                    reader_id=current_reader["Reader_ID"],
                    book_id=selected_book_id,
                    content=content,
                    rating=star_rating,
                )
                if success:
                    st.success("Review published to the community feed.")
                else:
                    st.error(message)

    with cancel_col:
        if st.button("Cancel", use_container_width=True, key="cr_cancel"):
            st.switch_page("pages/05_Book_Detail.py")
