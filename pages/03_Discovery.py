from html import escape
import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Backend.Functions.library_data import (
    get_books,
    get_genres,
    get_popular_books,
    get_reader_from_session,
    increment_book_clicked,
    update_recommendation_status,
)
from Backend.Functions.saved_books import save_book
from components.ui_helpers import (
    COLORS,
    inject_global_css,
    page_spacer,
    render_badge,
    render_book_cover,
    render_navbar,
    render_stars,
    section_title, render_navigation_section,
)


st.set_page_config(
    page_title="Discover",
    page_icon="LT",
    layout="wide",
    initial_sidebar_state="collapsed"
)

inject_global_css()
render_navbar(active_page="Discover")
page_spacer(20)

current_reader = None
if st.session_state.get("logged_in", False):
    current_reader = get_reader_from_session(st.session_state)


def save_discovery_book(book):
    if current_reader is None:
        st.warning("Please sign in before saving books.")
        return

    result = save_book(book["isbn"], current_reader["Reader_ID"])
    if result["success"]:
        update_recommendation_status(current_reader["Reader_ID"], book["isbn"], "saved")
        st.success("Saved.")
    else:
        st.info(result["message"])


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
        genre=active_genre,
        sort_option=sort_map[sort_label],
    )

    page_spacer(16)

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
                    f'<span class="muted">- {book["review_count"]} review(s)</span>',
                    unsafe_allow_html=True,
                )

            with cols[2]:
                page_spacer(10)
                st.markdown(
                    f'{render_badge(book["genre"], "beige")}<br><br>'
                    f'{render_badge("Database title", "available")}',
                    unsafe_allow_html=True,
                )

            with cols[3]:
                page_spacer(8)
                if st.button("Details", key=f"disc_detail_{book['id']}"):
                    increment_book_clicked(book["id"])
                    if current_reader:
                        update_recommendation_status(current_reader["Reader_ID"], book["id"], "clicked")
                    st.session_state["selected_book_id"] = book["id"]
                    st.switch_page("pages/15_Book_Detail.py")

                if st.button("Save", key=f"disc_save_{book['id']}"):
                    save_discovery_book(book)

                if st.button("Review", key=f"disc_review_{book['id']}"):
                    st.session_state["review_book_isbn"] = book["id"]
                    st.switch_page("pages/06_Create_Review.py")

        st.markdown("<hr>", unsafe_allow_html=True)

page_spacer(20)

section_title("Top 10 Popular Books")

popular_books = get_popular_books(limit=10)
if popular_books:
    for start in range(0, len(popular_books), 5):
        cols = st.columns(min(len(popular_books[start:start + 5]), 5))
        for offset, book in enumerate(popular_books[start:start + 5]):
            with cols[offset]:
                st.markdown(render_book_cover(book["cover"], "card"), unsafe_allow_html=True)
                st.markdown(
                    f'<span style="font-size:0.82rem; font-weight:600; color:{COLORS["dark_green"]};">'
                    f'{escape(book["title"])}</span><br>'
                    f'<span class="muted" style="font-size:0.75rem;">{escape(book["author"])}</span><br>'
                    f'{render_stars(book["avg_rating"])}',
                    unsafe_allow_html=True,
                )
                if st.button("Details", key=f"popular_detail_{book['id']}", use_container_width=True):
                    increment_book_clicked(book["id"])
                    if current_reader:
                        update_recommendation_status(current_reader["Reader_ID"], book["id"], "clicked")
                    st.session_state["selected_book_id"] = book["id"]
                    st.switch_page("pages/15_Book_Detail.py")
                if st.button("Save", key=f"popular_save_{book['isbn']}", use_container_width=True):
                    save_discovery_book(book)
else:
    st.info("No books are available for popularity ranking yet.")

page_spacer(20)

#--------------------------------------------------------------------NAVIGATION
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
section_title("Navigation")
render_navigation_section()
