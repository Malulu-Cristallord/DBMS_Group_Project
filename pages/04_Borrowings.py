# =============================================================================
# FILE: pages/04_Borrowings.py
# PURPOSE: Shows the user's current borrowings, reservations, and history.
# =============================================================================

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.ui_helpers import (
    inject_global_css, render_navbar, render_book_cover,
    render_badge, render_progress_bar, render_stars,
    page_spacer, section_title, COLORS,
)
from data.mock_data import CURRENT_BORROWINGS, PENDING_RESERVATIONS, READING_HISTORY

st.set_page_config(
    page_title="Borrowings — LibTrack",
    page_icon="📖",
    layout="wide",
)

inject_global_css()
render_navbar(active_page="borrowings")
page_spacer(20)

# Layout
sidebar_col, main_col = st.columns([1, 4])

# Sidebar navigation
with sidebar_col:
    if "borrow_section" not in st.session_state:
        st.session_state["borrow_section"] = "In progress"

    sections = ["In progress", "Reservations", "History"]

    for s in sections:
        if st.button(s, key=f"nav_{s}", use_container_width=True):
            st.session_state["borrow_section"] = s
            st.rerun()

# Main content
with main_col:
    active_section = st.session_state.get("borrow_section", "In progress")

    # =========================================================
    # IN PROGRESS
    # =========================================================
    if active_section == "In progress":
        section_title("Current borrowings")

        if CURRENT_BORROWINGS:
            for b in CURRENT_BORROWINGS:
                progress_pct = int((b["days_remaining"] / b["total_days"]) * 100)

                col1, col2, col3 = st.columns([0.6, 4, 1.2])

                with col1:
                    st.markdown(render_book_cover(b["cover_color"]), unsafe_allow_html=True)

                with col2:
                    st.markdown(
                        f"<strong>{b['title']}</strong><br>"
                        f"<span class='secondary'>{b['author']}</span><br>"
                        f"<span class='muted'>Due {b['due_date']} · {b['format']}</span>",
                        unsafe_allow_html=True
                    )
                    st.markdown(render_progress_bar(progress_pct), unsafe_allow_html=True)

                with col3:
                    if st.button("Renew", key=f"renew_{b['id']}"):
                        st.toast("Renewed")
                    if st.button("Return", key=f"return_{b['id']}"):
                        st.toast("Returned")

                st.markdown("<hr>", unsafe_allow_html=True)

        section_title("Pending reservations")

        if PENDING_RESERVATIONS:
            for r in PENDING_RESERVATIONS:
                col1, col2, col3 = st.columns([0.6, 4, 1.2])

                with col1:
                    st.markdown(render_book_cover(r["cover_color"]), unsafe_allow_html=True)

                with col2:
                    st.markdown(
                        f"<strong>{r['title']}</strong><br>"
                        f"<span class='secondary'>{r['author']}</span><br>",
                        unsafe_allow_html=True
                    )

                    st.markdown(
                        render_badge("Position " + str(r["queue_position"]) + " in queue", "waitlist"),
                        unsafe_allow_html=True
                    )

                    st.markdown(
                        f"<span class='muted'>Available in ~{r['estimated_days']} days</span>",
                        unsafe_allow_html=True
                    )

                with col3:
                    if st.button("Cancel", key=f"cancel_{r['id']}"):
                        st.toast("Cancelled")

                st.markdown("<hr>", unsafe_allow_html=True)

    # =========================================================
    # RESERVATIONS
    # =========================================================
    elif active_section == "Reservations":
        section_title("My reservations")

        if PENDING_RESERVATIONS:
            for r in PENDING_RESERVATIONS:
                col1, col2, col3 = st.columns([0.6, 4, 1.2])

                with col1:
                    st.markdown(render_book_cover(r["cover_color"]), unsafe_allow_html=True)

                with col2:
                    st.markdown(
                        f"<strong>{r['title']}</strong><br>"
                        f"<span class='secondary'>{r['author']}</span><br>",
                        unsafe_allow_html=True
                    )

                    st.markdown(
                        render_badge("Position " + str(r["queue_position"]) + " in queue", "waitlist"),
                        unsafe_allow_html=True
                    )

                with col3:
                    if st.button("Cancel", key=f"cancel2_{r['id']}"):
                        st.toast("Cancelled")

                st.markdown("<hr>", unsafe_allow_html=True)

    # =========================================================
    # HISTORY
    # =========================================================
    elif active_section == "History":
        section_title("Reading history")

        format_filter = st.selectbox(
            "Filter",
            ["All formats", "Physical", "E-book"]
        )

        filtered = READING_HISTORY
        if format_filter != "All formats":
            filtered = [h for h in filtered if h["format"] == format_filter]

        for item in filtered:
            col1, col2, col3 = st.columns([0.6, 4, 1])

            with col1:
                st.markdown(render_book_cover(item["cover_color"]), unsafe_allow_html=True)

            with col2:
                st.markdown(
                    f"<strong>{item['title']}</strong><br>"
                    f"<span class='secondary'>{item['author']}</span><br>"
                    f"<span class='muted'>Returned {item['returned_date']}</span>",
                    unsafe_allow_html=True
                )

            with col3:
                if st.button("Borrow again", key=f"again_{item['id']}"):
                    st.toast("Added")

            st.markdown("<hr>", unsafe_allow_html=True)