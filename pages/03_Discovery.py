from html import escape
import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Backend.Functions.library_data import get_books, get_genres
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
    page_title="Discover | LibTrack",
    page_icon="LT",
    layout="wide",
)

inject_global_css()
render_navbar(active_page="discover")
page_spacer(20)


sidebar_col, main_col = st.columns([1, 4])

with sidebar_col:
    st.markdown(
        f'<p style="font-size:0.75rem; font-weight:600; color:{COLORS["text_muted"]}; '
        'text-transform:uppercase; margin-bottom:10px;">Categories</p>',
        unsafe_allow_html=True,
    )

    genres = get_genres(include_all=True)
    if "active_genre" not in st.session_state:
        st.session_state["active_genre"] = "All genres"

    for genre in genres:
        if st.button(genre, key=f"genre_{genre}", use_container_width=True):
            st.session_state["active_genre"] = genre
            st.rerun()


with main_col:
    search_col, sort_col = st.columns([3, 1])

    with search_col:
        search_query = st.text_input(
            "",
            value=st.session_state.pop("book_search_query", ""),
            placeholder="Search by title, author, or genre...",
            label_visibility="collapsed",
            key="disc_search",
        )

    with sort_col:
        sort_label = st.selectbox(
            "",
            options=["Sort by rating", "Sort by title", "Sort by year"],
            label_visibility="collapsed",
            key="disc_sort",
        )

    sort_map = {
        "Sort by rating": "rating",
        "Sort by title": "title",
        "Sort by year": "year",
    }

    active_genre = st.session_state.get("active_genre", "All genres")
    filtered_books = get_books(
        search_query=search_query,
        category=active_genre,
        sort_option=sort_map[sort_label],
    )

    page_spacer(16)

    section_title("Popular this week")

    popular_books = get_books(category=active_genre, sort_option="rating", limit=6)
    if popular_books:
        cols = st.columns(min(len(popular_books), 6))
        for index, book in enumerate(popular_books):
            with cols[index]:
                st.markdown(render_book_cover(book["cover"], "card"), unsafe_allow_html=True)
                st.markdown(
                    f'<span style="font-size:0.82rem; font-weight:600; color:{COLORS["dark_green"]};">'
                    f'{escape(book["title"])}</span><br>'
                    f'<span class="muted" style="font-size:0.75rem;">{escape(book["author"])}</span>',
                    unsafe_allow_html=True,
                )
    else:
        st.info("No books match the current filter.")

    page_spacer(20)
    st.markdown("<hr>", unsafe_allow_html=True)

    section_title("Recommended by the community")

    if not filtered_books:
        st.info("No books found. Add books to the database to populate discovery.")

    for book in filtered_books:
        with st.container():
            cols = st.columns([0.5, 4, 2, 1])

            with cols[0]:
                page_spacer(6)
                st.markdown(render_book_cover(book["cover"]), unsafe_allow_html=True)

            with cols[1]:
                st.markdown(
                    f'<strong style="font-size:1rem; color:{COLORS["dark_green"]};">'
                    f'{escape(book["title"])}</strong><br>'
                    f'<span class="secondary">{escape(book["author"])}</span><br>'
                    f'{render_stars(book["avg_rating"])} '
                    f'<span class="muted">- {book["review_count"]} posts</span>',
                    unsafe_allow_html=True,
                )

            with cols[2]:
                page_spacer(10)
                st.markdown(
                    f'{render_badge(book["category"], "beige")}<br><br>'
                    f'{render_badge("Database title", "available")}',
                    unsafe_allow_html=True,
                )

            with cols[3]:
                page_spacer(8)
                if st.button("Details", key=f"disc_detail_{book['id']}"):
                    st.session_state["selected_book_id"] = book["id"]
                    st.switch_page("pages/05_Book_Detail.py")

                if st.button("Review", key=f"disc_review_{book['id']}"):
                    st.session_state["review_book_id"] = book["id"]
                    st.switch_page("pages/06_Create_Review.py")

        st.markdown("<hr>", unsafe_allow_html=True)
