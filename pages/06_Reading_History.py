# =============================================================================
# FILE: pages/06_Reading_History.py
# PURPOSE: Displays the user's full reading history and personal reading habits.
#
# FUTURE BACK-END INTEGRATION:
#   - History: GET /api/borrowings?user_id=<id>&status=returned
#   - Habits/stats: GET /api/stats/reading-habits?user_id=<id>
#   - Borrow again: POST /api/borrowings { book_id }
#   - Filter by format: GET /api/borrowings?format=Physical|E-book
# =============================================================================

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.ui_helpers import (
    inject_global_css, render_navbar, render_book_cover,
    render_stars, render_badge, render_progress_bar,
    page_spacer, section_title, COLORS,
)
from data.mock_data import READING_HISTORY, CURRENT_USER

st.set_page_config(
    page_title="Reading History — LibTrack",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed",
)
inject_global_css()
render_navbar(active_page="my_library")
page_spacer(20)

# Layout: sidebar + main + habits
sidebar_col, main_col, habits_col = st.columns([1, 3, 1.5])

# =============================================================================
# SIDEBAR NAVIGATION
# =============================================================================
with sidebar_col:
    menu_items = ["My profile", "My borrowings", "My posts", "History"]
    for item in menu_items:
        is_active = item == "History"
        if st.button(item, key=f"hist_nav_{item}", use_container_width=True):
            if item == "My profile":
                st.switch_page("pages/08_Profile.py")
            elif item == "My borrowings":
                st.switch_page("pages/04_Borrowings.py")
            elif item == "My posts":
                st.switch_page("pages/05_Posts_Reviews.py")

# =============================================================================
# MAIN CONTENT — Reading history list
# =============================================================================
with main_col:
    hist_title_col, filter_col = st.columns([2, 1])
    with hist_title_col:
        section_title("Reading history")
    with filter_col:
        # In production: format filter sent as query param to the API
        format_filter = st.selectbox(
            "",
            ["All formats", "Physical", "E-book"],
            label_visibility="collapsed",
            key="rh_format",
        )

    # Filter history
    filtered = READING_HISTORY
    if format_filter != "All formats":
        filtered = [h for h in filtered if h["format"] == format_filter]

    # Group by month and display
    months_seen = []
    for item in filtered:
        if item["month"] not in months_seen:
            months_seen.append(item["month"])

    for month in months_seen:
        st.markdown(
            f'<p style="font-size:0.75rem; font-weight:700; letter-spacing:0.12em; '
            f'color:{COLORS["text_muted"]}; text-transform:uppercase; '
            f'margin-top:20px; margin-bottom:10px;">{month}</p>',
            unsafe_allow_html=True,
        )

        month_items = [h for h in filtered if h["month"] == month]
        for item in month_items:
            row = st.columns([0.5, 3, 1.5, 1])

            with row[0]:
                page_spacer(4)
                st.markdown(render_book_cover(item["cover_color"]), unsafe_allow_html=True)

            with row[1]:
                st.markdown(
                    f'<strong style="color:{COLORS["dark_green"]}; font-size:0.95rem;">'
                    f'{item["title"]}</strong><br>'
                    f'<span class="secondary">{item["author"]}</span><br>'
                    f'<span class="muted">Borrowed {item["borrowed_date"]} · '
                    f'Returned {item["returned_date"]} · {item["format"]}</span>',
                    unsafe_allow_html=True,
                )

            with row[2]:
                page_spacer(8)
                if item.get("rating"):
                    st.markdown(render_stars(item["rating"]), unsafe_allow_html=True)

            with row[3]:
                page_spacer(4)
                # In production: POST /api/borrowings { book_id: item["book_id"] }
                if st.button("Borrow again", key=f"rh_again_{item['id']}", use_container_width=True):
                    st.toast(f"'{item['title']}' added to borrowing queue!")

            st.markdown('<hr>', unsafe_allow_html=True)

# =============================================================================
# RIGHT PANEL — Reading habits summary
# In production: GET /api/stats/habits?user_id=<id>
# =============================================================================
with habits_col:
    section_title("My habits")

    # Preferred format
    st.markdown(
        f'<p class="muted" style="margin-bottom:4px;">Preferred format</p>'
        f'<strong style="font-size:1.1rem; color:{COLORS["dark_green"]};">Physical</strong><br>'
        f'<span class="muted">68% of borrowings</span>',
        unsafe_allow_html=True,
    )
    st.markdown(render_progress_bar(68), unsafe_allow_html=True)

    page_spacer(16)

    # Favourite genre
    fav_genre = CURRENT_USER["preferred_genres"][0] if CURRENT_USER["preferred_genres"] else "Unknown"
    st.markdown(
        f'<p class="muted" style="margin-bottom:4px;">Favourite genre</p>'
        f'<strong style="font-size:1.1rem; color:{COLORS["dark_green"]};">{fav_genre}</strong><br>'
        f'<span class="muted">42% of reads</span>',
        unsafe_allow_html=True,
    )
    st.markdown(render_progress_bar(42), unsafe_allow_html=True)

    page_spacer(16)

    # Total books read this year
    st.markdown(
        f'<p class="muted" style="margin-bottom:4px;">Total 2026</p>'
        f'<span style="font-family: \'Playfair Display\', Georgia, serif; '
        f'font-size:2rem; font-weight:700; color:{COLORS["dark_green"]};">'
        f'{CURRENT_USER["books_borrowed"]}</span><br>'
        f'<span class="muted">books borrowed</span>',
        unsafe_allow_html=True,
    )