import os
import sys

import streamlit as st

from Backend.Functions.book_request import check_for_badge_book_adding
from Backend.Functions.library_data import increment_book_clicked, update_recommendation_status, get_reader_from_session

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Backend.Functions import book_request
from components.ui_helpers import inject_global_css, page_spacer, render_navbar, render_navigation_section, \
    section_title

st.set_page_config(
    page_title="Add Books | LibTrack",
    page_icon="LT",
    layout="wide",
    initial_sidebar_state="collapsed"
)

inject_global_css()
render_navbar()
page_spacer(50)

current_reader = get_reader_from_session(st.session_state)

_, center_col, _ = st.columns([1, 1.4, 1])

with center_col:
    st.markdown(
        '<div style="text-align:center; margin-bottom:32px;">'
        '<span style="font-size:2.5rem;">LT</span><br>'
        '<h1 style="font-size:1.8rem; margin-top:8px;">Add to the collection</h1>'
        '<p class="muted">Type an ISBN to import book data from Open Library.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    isbn_input = st.text_input(
        "ISBN",
        placeholder="9780439362139",
        key="ISBN",
    )
    clean_isbn = isbn_input.strip().replace("-","")

    if st.button("Submit", type="primary"):
        if not clean_isbn:
            st.error("Please enter an ISBN.")
        if not clean_isbn.isdigit():
            st.error("Please enter 13 digit ISBN(Dashes are allowed).")
        else:
            result = book_request.request_book_data(clean_isbn)
            if result == "error":
                st.error(f"Error entering book for ISBN: {clean_isbn}")
            elif result == -1:
                st.error("This book already exists in our database.")
            else:
                st.success(f"Book data ({result['title']})imported into our system database.\n Thank you for your contribution!")
                check_for_badge_book_adding(current_reader["Reader_ID"])

page_spacer(20)
#--------------------------------------------------------------------NAVIGATION
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
section_title("Navigation")
render_navigation_section()