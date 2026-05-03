import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Backend.Functions.library_data import get_reader_from_session
from components.ui_helpers import inject_global_css, page_spacer, render_navbar, section_title


st.set_page_config(
    page_title="Borrowings | LibTrack",
    page_icon="LT",
    layout="wide",
)

inject_global_css()
render_navbar(active_page="borrowings")
page_spacer(20)


current_reader = get_reader_from_session(st.session_state)
if current_reader is None:
    st.warning("Please sign in to view reader borrowings.")
    if st.button("Go to Login", type="primary"):
        st.switch_page("pages/01_Login.py")
    st.stop()


sidebar_col, main_col = st.columns([1, 4])

with sidebar_col:
    if "borrow_section" not in st.session_state:
        st.session_state["borrow_section"] = "In progress"

    for section in ["In progress", "Reservations", "History"]:
        if st.button(section, key=f"nav_{section}", use_container_width=True):
            st.session_state["borrow_section"] = section
            st.rerun()


with main_col:
    active_section = st.session_state.get("borrow_section", "In progress")

    if active_section == "In progress":
        section_title("Current borrowings")
        st.info(
            "No borrowings table is defined yet. This page is connected to the current reader, "
            "but borrowing records need a database table before real rows can appear."
        )

    elif active_section == "Reservations":
        section_title("My reservations")
        st.info(
            "No reservations table is defined yet. Add a reservations table linked to "
            "readers.Reader_ID to enable this view."
        )

    else:
        section_title("Reading history")
        if current_reader.get("Show_Reading_History"):
            st.info(
                "No borrowing history table is defined yet. Reader privacy is loaded from "
                "readers.Show_Reading_History."
            )
        else:
            st.warning("This reader has disabled reading history visibility.")
