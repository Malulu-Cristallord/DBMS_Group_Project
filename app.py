from html import escape
import os
import sys

import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))

from Backend.Functions.library_data import (
    get_book_by_id,
    get_books,
    get_posts,
    get_reader_from_session,
    get_recommended_books,
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
    page_title="LibTrack | Home",
    page_icon="LT",
    layout="wide",
)

inject_global_css()


if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    render_navbar(active_page="discover")
    page_spacer(40)
    st.warning("Please sign in to access your LibTrack home page.")

    if st.button("Go to Login", type="primary"):
        st.switch_page("pages/01_Login.py")

    st.stop()


current_reader = get_reader_from_session(st.session_state)

if current_reader is None:
    render_navbar(active_page="discover")
    page_spacer(40)
    st.error("Could not load your reader profile. Please log in again.")

    if st.button("Go to Login", type="primary"):
        st.session_state.clear()
        st.switch_page("pages/01_Login.py")

    st.stop()


render_navbar(active_page="discover")
page_spacer(24)

col_welcome, col_action = st.columns([3, 1])

with col_welcome:
    reader_first_name = (current_reader["Name"] or "reader").split()[0]
    st.markdown(
        f'<h1 style="margin-bottom:4px;">Welcome back, {escape(reader_first_name)}</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="secondary">Discover your next great read and share your journey.</p>',
        unsafe_allow_html=True,
    )

with col_action:
    page_spacer(10)
    if st.button("Create a post", type="primary", use_container_width=True):
        st.switch_page("pages/07_Create_Post.py")


page_spacer(10)

search_query = st.text_input(
    "",
    placeholder="Search for a book, author, or genre...",
    label_visibility="collapsed",
    key="home_search",
)

if search_query:
    st.session_state["book_search_query"] = search_query
    st.info(f"Searching for: **{search_query}**. Open Book Discovery for full results.")

    if st.button("Open Book Discovery"):
        st.switch_page("pages/03_Discovery.py")


page_spacer(20)
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

section_title("Recommended for you")

recommended_books = get_recommended_books(current_reader, limit=4)

if not recommended_books:
    st.info("No recommended books found yet. Add books to the database or update your preferred categories.")
else:
    rec_cols = st.columns(min(len(recommended_books), 4))

    for index, book in enumerate(recommended_books[:4]):
        with rec_cols[index]:
            st.markdown(render_book_cover(book["cover"], size="card"), unsafe_allow_html=True)
            st.markdown(
                f'<strong style="font-size:0.9rem; color:{COLORS["dark_green"]};">'
                f'{escape(book["title"])}</strong>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<span class="muted">{escape(book["author"])}</span><br>'
                f'{render_stars(book["avg_rating"])}',
                unsafe_allow_html=True,
            )

            if st.button("View", key=f"rec_{book['id']}", use_container_width=True):
                st.session_state["selected_book_id"] = book["id"]
                st.switch_page("pages/05_Book_Detail.py")


page_spacer(20)
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

if st.button("Find books", type="primary"):
    st.switch_page("pages/03_Discovery.py")


section_title("Popular this week")

popular_books = get_books(sort_option="rating", limit=6)

if not popular_books:
    st.info("No books found yet. Please insert book data into the books table.")
else:
    pop_cols = st.columns(min(len(popular_books), 6))

    for index, book in enumerate(popular_books[:6]):
        with pop_cols[index]:
            st.markdown(render_book_cover(book["cover"], size="card"), unsafe_allow_html=True)
            st.markdown(
                f'<span style="font-size:0.8rem; font-weight:600; color:{COLORS["dark_green"]};">'
                f'{escape(book["title"])}</span><br>'
                f'<span class="muted" style="font-size:0.75rem;">{escape(book["author"])}</span>',
                unsafe_allow_html=True,
            )


page_spacer(20)
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

section_title("Activity feed")

activity_posts = get_posts(limit=10)

if not activity_posts:
    st.info("No activity yet. Reviews will appear here after readers create posts.")
else:
    for post in activity_posts:
        rating_html = render_stars(post["rating"]) if post.get("rating") else ""
        reader_name = post.get("reader_name") or "Unknown reader"
        book_title = post.get("book_title") or "an unlinked book"
        content = post.get("content") or "No content."

        col_post, col_tag = st.columns([5, 1])

        with col_post:
            st.markdown(
                f"""
                <div class="card">
                    <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
                        {render_avatar(reader_initials(reader_name), COLORS["sage"] if "sage" in COLORS else COLORS["light_green"], COLORS["dark_green"])}
                        <div>
                            <strong style="font-size:0.95rem;">{escape(reader_name)}</strong>
                            <span class="muted">
                                reviewed <strong>{escape(book_title)}</strong> on {escape(str(post.get("created_at") or ""))}
                            </span>
                        </div>
                        <div style="margin-left:auto;">{rating_html}</div>
                    </div>
                    <p style="margin:6px 0 10px 0; font-size:0.92rem; line-height:1.55;">
                        {escape(content)}
                    </p>
                    <div class="action-row">
                        {int(post.get("upvote_count") or 0)} likes
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_tag:
            page_spacer(8)
            st.markdown(render_badge("Review", style="beige"), unsafe_allow_html=True)

            if st.button("Details", key=f"feed_detail_{post['post_id']}"):
                selected_book = get_book_by_id(post.get("book_id"))
                if selected_book:
                    st.session_state["selected_book_id"] = selected_book["id"]
                    st.switch_page("pages/05_Book_Detail.py")
                else:
                    st.toast("This post is not linked to a book.")


page_spacer(20)
