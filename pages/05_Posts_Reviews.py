from html import escape
import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Backend.Functions.library_data import (
    create_post,
    get_books,
    get_posts,
    get_reader_from_session,
    reader_initials,
)
from components.ui_helpers import (
    COLORS,
    inject_global_css,
    page_spacer,
    render_avatar,
    render_badge,
    render_book_cover,
    render_navbar,
    render_stars,
    section_title,
)


st.set_page_config(
    page_title="Posts & Reviews | LibTrack",
    page_icon="LT",
    layout="wide",
)

inject_global_css()
render_navbar(active_page="my_library")
page_spacer(20)


current_reader = get_reader_from_session(st.session_state)
if current_reader is None:
    st.warning("Please sign in before publishing posts or reviews.")
    if st.button("Go to Login", type="primary"):
        st.switch_page("pages/01_Login.py")
    st.stop()


sidebar_col, main_col = st.columns([1, 4])

with sidebar_col:
    menu_items = ["My profile", "My borrowings", "My posts", "History"]
    for item in menu_items:
        if st.button(item, key=f"posts_nav_{item}", use_container_width=True):
            if item == "My profile":
                st.switch_page("pages/08_Profile.py")
            elif item == "My borrowings":
                st.switch_page("pages/04_Borrowings.py")
            elif item == "History":
                st.switch_page("pages/06_Reading_History.py")


with main_col:
    section_title("Write a review")

    books = get_books(sort_option="title")
    if books:
        book_options = {f'{book["title"]} - {book["author"]}': book["id"] for book in books}
        selected_book_label = st.selectbox(
            "Select a book",
            options=list(book_options.keys()),
            key="review_book_sel",
            label_visibility="collapsed",
        )
        selected_book_id = book_options[selected_book_label]
        selected_book = next(book for book in books if str(book["id"]) == str(selected_book_id))

        mini_col1, mini_col2 = st.columns([0.4, 4])
        with mini_col1:
            st.markdown(render_book_cover(selected_book["cover"]), unsafe_allow_html=True)
        with mini_col2:
            st.markdown(
                f'<strong style="color:{COLORS["dark_green"]};">{escape(selected_book["title"])}</strong><br>'
                f'<span class="muted">{escape(selected_book["author"])}</span>',
                unsafe_allow_html=True,
            )

        page_spacer(8)

        review_rating = st.select_slider(
            "Your rating",
            options=[1, 2, 3, 4, 5],
            value=4,
            format_func=lambda value: f"{value}/5",
            key="review_stars",
        )

        review_text = st.text_area(
            "Your review",
            placeholder="Share your reading experience...",
            height=120,
            label_visibility="collapsed",
            key="review_text_input",
        )

        if st.button("Publish", type="primary", key="publish_review", use_container_width=True):
            success, message = create_post(
                reader_id=current_reader["Reader_ID"],
                book_id=selected_book_id,
                content=review_text,
                rating=review_rating,
            )
            if success:
                st.success("Review published successfully.")
            else:
                st.error(message)
    else:
        st.info("No books are available in the database yet.")

    page_spacer(16)
    st.markdown("<hr>", unsafe_allow_html=True)

    section_title("Activity feed")

    posts = get_posts(limit=30)
    if not posts:
        st.info("No posts have been published yet.")

    for post in posts:
        reader_name = post.get("reader_name") or "Unknown reader"
        book_title = post.get("book_title") or "an unlinked book"
        rating_html = render_stars(post["rating"]) if post.get("rating") else ""

        row_main, row_tag = st.columns([5, 1])
        with row_main:
            st.markdown(
                f"""
                <div class="card">
                    <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
                        {render_avatar(reader_initials(reader_name), COLORS["light_green"], COLORS["dark_green"])}
                        <div style="flex:1;">
                            <strong>{escape(reader_name)}</strong>
                            <span class="muted"> reviewed <strong>{escape(book_title)}</strong> on {escape(str(post.get("created_at") or ""))}</span>
                        </div>
                        <div>{rating_html}</div>
                    </div>
                    <p style="font-size:0.92rem; line-height:1.55; margin:6px 0 10px 0;">
                        {escape(post.get("content") or "")}
                    </p>
                    <span class="action-row">{int(post.get("upvote_count") or 0)} likes</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with row_tag:
            page_spacer(10)
            st.markdown(render_badge("Post", "beige"), unsafe_allow_html=True)
