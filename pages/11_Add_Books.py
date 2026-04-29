import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.ui_helpers import inject_global_css, render_navbar, page_spacer, COLORS
from Backend.Functions import book_request

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="Login — LibTrack",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed",
)
inject_global_css()
render_navbar()
page_spacer(50)

# Initiate session state
if "ISBN" not in st.session_state:
    st.session_state["ISBN"] = ""


_, center_col, _ = st.columns([1, 1.4, 1])

with center_col:
    # Logo and title
    st.markdown(
        f'<div style="text-align:center; margin-bottom:32px;">'
        f'<span style="font-size:2.5rem;">📖</span><br>'
        f'<h1 style="font-size:1.8rem; margin-top:8px;">Adding more to the collection?k</h1>'
        f'<p class="muted">Type in the ISBN of your book to add books from open database</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    isbn_input = st.text_input(
        "ISBN",
        placeholder="e.g.: 9780439362139",
        key="ISBN",
    )

    if st.button("Submit"):
        if isbn_input != "":
            st.session_state["ISBN"] = isbn_input
            book_request.request_book_data(isbn_input)

