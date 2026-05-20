from html import escape
import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Backend.Functions.library_data import get_posts, get_reader_from_session
from components.ui_helpers import (
    COLORS,
    inject_global_css,
    page_spacer,
    render_badge,
    render_book_cover,
    render_login_required,
    render_navbar,
    render_stars,
    section_title,
)


st.set_page_config(
    page_title="Reading History | LibTrack",
    page_icon="LT",
    layout="wide",
)

inject_global_css()
render_navbar(active_page="my_library")
page_spacer(20)


current_reader = get_reader_from_session(st.session_state)
if current_reader is None:
    render_login_required("Please sign in to view reading history.")
    st.stop()


section_title("My Saved Books")
