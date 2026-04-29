# =============================================================================
# FILE: pages/03_Discovery.py (shown as "2. Discovery" in the UI)
# PURPOSE: Book discovery page — browse, search, filter, and sort books.
#
# FUTURE BACK-END INTEGRATION:
#   - Search/filter/sort values → GET /api/books?search=&category=&sort=
#   - View Details → navigate to /books/<book_id>
#   - Borrow / Reserve → POST /api/borrowings or POST /api/reservations
#   - Wishlist → POST /api/wishlist
# =============================================================================

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.ui_helpers import (
    inject_global_css, render_navbar, render_book_cover,
    render_stars, render_badge, page_spacer, section_title, COLORS,
)
from data.mock_data import BOOKS, GENRES

st.set_page_config(
    page_title="Discover — LibTrack",
    page_icon="📖",
    layout="wide",
)
inject_global_css()
render_navbar(active_page="discover")
page_spacer(20)

# =============================================================================
# TWO-COLUMN LAYOUT: Sidebar (categories) + Main content
# =============================================================================
sidebar_col, main_col = st.columns([1, 4])

# =============================================================================
# LEFT SIDEBAR — Category filter
# In production: each click sends category value to GET /api/books?category=
# =============================================================================
with sidebar_col:
    st.markdown(
        f'<p style="font-size:0.75rem; font-weight:600; letter-spacing:0.1em; '
        f'color:{COLORS["text_muted"]}; text-transform:uppercase; margin-bottom:10px;">'
        f'CATEGORIES</p>',
        unsafe_allow_html=True,
    )

    # Session state to track active genre
    if "active_genre" not in st.session_state:
        st.session_state["active_genre"] = "All genres"

    for genre in GENRES:
        is_active = st.session_state["active_genre"] == genre
        btn_style = (
            f"background-color:{COLORS['light_green']}; color:{COLORS['dark_green']}; "
            f"border-left:3px solid {COLORS['dark_green']}; font-weight:600;"
        ) if is_active else "color:#3A3A3A;"

        if st.button(
            genre,
            key=f"genre_{genre}",
            use_container_width=True,
        ):
            st.session_state["active_genre"] = genre
            st.rerun()

# =============================================================================
# MAIN CONTENT AREA
# =============================================================================
with main_col:

    # -------------------------------------------------------------------------
    # SEARCH + SORT ROW
    # In production: search_query → GET /api/books?search=<query>
    #                sort_option  → GET /api/books?sort=<popularity|rating|relevance>
    # -------------------------------------------------------------------------
    search_col, sort_col = st.columns([3, 1])
    with search_col:
        search_query = st.text_input(
            "",
            placeholder="🔍  Search by title, author, or keyword...",
            label_visibility="collapsed",
            key="disc_search",
        )
    with sort_col:
        sort_option = st.selectbox(
            "",
            options=["Sort by popularity", "Sort by rating", "Sort by relevance"],
            label_visibility="collapsed",
            key="disc_sort",
        )

    page_spacer(16)

    # -------------------------------------------------------------------------
    # Filter books based on active genre and search query
    # -------------------------------------------------------------------------
    active_genre = st.session_state.get("active_genre", "All genres")
    filtered_books = BOOKS

    if active_genre != "All genres":
        filtered_books = [b for b in filtered_books if b["category"] == active_genre]

    if search_query:
        q = search_query.lower()
        filtered_books = [
            b for b in filtered_books
            if q in b["title"].lower() or q in b["author"].lower()
        ]

    # Sort
    if sort_option == "Sort by rating":
        filtered_books = sorted(filtered_books, key=lambda x: x["avg_rating"], reverse=True)
    elif sort_option == "Sort by popularity":
        filtered_books = sorted(filtered_books, key=lambda x: x["review_count"], reverse=True)

    # -------------------------------------------------------------------------
    # POPULAR THIS WEEK — horizontal book cover grid
    # In production: GET /api/books/popular?period=week&category=<active_genre>
    # -------------------------------------------------------------------------
    section_title("Popular this week")

    pop_books = [b for b in filtered_books if b.get("popular")][:6]
    if pop_books:
        cols = st.columns(min(len(pop_books), 6))
        for i, book in enumerate(pop_books):
            with cols[i]:
                st.markdown(render_book_cover(book["cover_color"], "card"), unsafe_allow_html=True)
                st.markdown(
                    f'<span style="font-size:0.82rem; font-weight:600; '
                    f'color:{COLORS["dark_green"]};">{book["title"]}</span><br>'
                    f'<span class="muted" style="font-size:0.75rem;">{book["author"]}</span>',
                    unsafe_allow_html=True,
                )
    else:
        st.info("No popular books match the current filter.")

    page_spacer(20)
    st.markdown('<hr>', unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # RECOMMENDED BY THE COMMUNITY — list view
    # In production: GET /api/books/community-picks
    # -------------------------------------------------------------------------
    section_title("Recommended by the community")

    for book in filtered_books:
        # Determine availability
        physical_avail = book.get("physical_available", "—")
        is_available = physical_avail != "0 / 2" and physical_avail != "0 / 3"

        avail_label = "Available" if is_available else "Waitlist"
        avail_style = "available" if is_available else "waitlist"
        action_label = "Borrow" if is_available else "Reserve"

        with st.container():
            cols = st.columns([0.5, 4, 2, 1])

            with cols[0]:
                page_spacer(6)
                st.markdown(render_book_cover(book["cover_color"]), unsafe_allow_html=True)

            with cols[1]:
                st.markdown(
                    f'<strong style="font-size:1rem; color:{COLORS["dark_green"]};">'
                    f'{book["title"]}</strong><br>'
                    f'<span class="secondary">{book["author"]}</span><br>'
                    f'{render_stars(book["avg_rating"])} '
                    f'<span class="muted">· {book["review_count"]} reviews</span>',
                    unsafe_allow_html=True,
                )

            with cols[2]:
                page_spacer(10)
                st.markdown(
                    f'{render_badge(avail_label, avail_style)}'
                    f'<br><br>{render_badge(book["formats"][0], "beige")}',
                    unsafe_allow_html=True,
                )

            with cols[3]:
                page_spacer(8)
                # In production: this button calls POST /api/borrowings or POST /api/reservations
                btn_type = "primary" if is_available else "secondary"
                if st.button(action_label, key=f"disc_borrow_{book['id']}",
                             type="primary" if is_available else "secondary"):
                    if is_available:
                        st.toast(f"'{book['title']}' borrowed successfully!")
                    else:
                        st.toast(f"Reserved! You are in the queue for '{book['title']}'.")

                # In production: POST /api/wishlist with book_id
                if st.button("+ Wishlist", key=f"disc_wish_{book['id']}"):
                    st.toast(f"'{book['title']}' added to your wishlist.")

                # In production: navigate to /books/<book_id>
                if st.button("Details", key=f"disc_detail_{book['id']}"):
                    st.session_state["selected_book_id"] = book["id"]
                    st.switch_page("pages/05_Book_Detail.py")

        st.markdown('<hr>', unsafe_allow_html=True)