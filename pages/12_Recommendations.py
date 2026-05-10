from html import escape
import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Backend.Functions.library_data import (
    generate_recommendations_for_reader,
    get_recommendations_for_reader,
    get_reader_from_session,
    increment_book_clicked,
    increment_book_saved,
    update_recommendation_status,
)
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
    page_title="Recommendations | LibTrack",
    page_icon="LT",
    layout="wide",
)

inject_global_css()
render_navbar(active_page="discover")
page_spacer(24)


current_reader = get_reader_from_session(st.session_state)
if current_reader is None:
    st.warning("Please sign in to view recommendations.")
    if st.button("Go to Login", type="primary"):
        st.switch_page("pages/01_Login.py")
    st.stop()


section_title("Recommendations")

preferred_category = current_reader.get("Preferred_Category") or "Not set"
st.markdown(
    f'<p class="muted">Preferred category: {escape(str(preferred_category))}</p>',
    unsafe_allow_html=True,
)

if st.button("Generate Recommendations", type="primary"):
    generated = generate_recommendations_for_reader(current_reader["Reader_ID"], limit=10)
    if generated:
        st.success("Recommendations generated.")
    else:
        st.warning("No recommendations were generated. Check that books and recommendations tables exist.")


page_spacer(16)

recommendations = get_recommendations_for_reader(current_reader["Reader_ID"], limit=10)

if not recommendations:
    st.info("No recommendations yet. Generate recommendations to create rows in the database.")

for book in recommendations:
    cover_col, body_col, action_col = st.columns([0.6, 4, 1.2])

    with cover_col:
        st.markdown(render_book_cover(book["cover"]), unsafe_allow_html=True)

    with body_col:
        st.markdown(
            f'<strong style="color:{COLORS["dark_green"]};">{escape(book["title"])}</strong><br>'
            f'<span class="secondary">{escape(book["author"])} - {escape(book["category"])}</span><br>'
            f'{render_stars(book["avg_rating"])} '
            f'<span class="muted">score {book["score"]:.4f}</span><br>'
            f'<span class="muted">{escape(book["reason"])}</span><br>'
            f'{render_badge(book["recommendation_status"] or "unread", "beige")}',
            unsafe_allow_html=True,
        )

    with action_col:
        if st.button("View", key=f'view_{book["isbn"]}', use_container_width=True):
            increment_book_clicked(book["isbn"])
            update_recommendation_status(current_reader["Reader_ID"], book["isbn"], "clicked")
            st.session_state["selected_book_id"] = book["isbn"]
            st.switch_page("pages/15_Book_Detail.py")

        if st.button("Save", key=f'save_{book["isbn"]}', use_container_width=True):
            increment_book_saved(book["isbn"])
            update_recommendation_status(current_reader["Reader_ID"], book["isbn"], "saved")
            st.success("Saved.")

    st.markdown("<hr>", unsafe_allow_html=True)
