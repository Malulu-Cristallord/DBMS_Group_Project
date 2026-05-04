import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Backend.Functions import book_request
from components.ui_helpers import inject_global_css, page_spacer, render_navbar


st.set_page_config(
    page_title="Add Books | LibTrack",
    page_icon="LT",
    layout="wide",
)

inject_global_css()
render_navbar()
page_spacer(50)


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

    if st.button("Submit", type="primary"):
        if not isbn_input.strip():
            st.error("Please enter an ISBN.")
        else:
            result = book_request.request_book_data(isbn_input.strip())
            if isinstance(result, dict) and result.get("error"):
                st.error(result["error"])
            else:
                st.success("Book data imported into our system database.\n Thank you for your contribution!")
