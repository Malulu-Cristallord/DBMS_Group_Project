from html import escape
import os
import sys

import streamlit as st
from requests import delete

from Backend.Functions.saved_books import delete_saved_book, get_saved_books

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Backend.Functions.library_data import (
    generate_recommendations_for_reader,
    get_recommendations_for_reader,
    get_reader_from_session,
    increment_book_clicked,
    increment_book_saved,
    update_recommendation_status, decrement_book_saved,
)
from Backend.Functions.saved_books import(
    save_book,
)
from components.ui_helpers import (
    COLORS,
    inject_global_css,
    page_spacer,
    render_badge,
    render_book_cover,
    render_login_required,
    render_navbar,
    render_stars,
    section_title, render_navigation_section,
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
    render_login_required("Please sign in to view recommendations.")
    st.stop()


section_title("Saved Books")

st.markdown(
    f'<p class="muted">Books that you have interest in</p>',
    unsafe_allow_html=True,
)

page_spacer(16)

saved_books = get_saved_books(current_reader["Reader_ID"])

if not saved_books:
    st.info("No books saved. How about we discover a little?")
    if st.button("Let's go and find some books to read", type="primary", use_container_width=True):
        st.switch_page("pages/03_Discovery.py")
else:
    for book in saved_books:
        cover_col, body_col, action_col = st.columns([0.6, 4, 1.2])

        with cover_col:
            st.markdown(render_book_cover(book["cover"]), unsafe_allow_html=True)

        with body_col:
            st.markdown(
                f'<strong style="color:{COLORS["dark_green"]};">{escape(book["title"])}</strong><br>'
                f'<span class="secondary">{escape(book["author"])} - {escape(book["genre"])}</span><br>'
                f'{render_stars(book["avg_rating"])}',
                unsafe_allow_html=True,
            )

        with action_col:
            if st.button("View", key=f'view_{book["isbn"]}', use_container_width=True):
                update_recommendation_status(current_reader["Reader_ID"], book["isbn"], "clicked")
                st.session_state["selected_book_id"] = book["isbn"]
                st.switch_page("pages/15_Book_Detail.py")
            if st.button("Delete from save", key=f'delete_{book["isbn"]}', use_container_width=True):
                st.session_state["selected_book_id"] = book["isbn"]
                if delete_saved_book(current_reader["Reader_ID"], book["isbn"]):
                    decrement_book_saved(book['isbn'])
                    delete_saved_book(book["isbn"], current_reader["Reader_ID"])
                    success_message = f"Deleted book {book['title']} from saved books successfully."
                    st.success(success_message)
                else:
                    success_message = f"Book {book['title']} was not deleted. An error has likely occurred"

        st.markdown("<hr>", unsafe_allow_html=True)

page_spacer(20)
#--------------------------------------------------------------------NAVIGATION
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
section_title("Navigation")
render_navigation_section()