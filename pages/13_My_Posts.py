from html import escape
import os
import sys

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from Backend.Functions.post_handler import (
    get_posts_by_reader,
    delete_post,
)
from Backend.Functions.library_data import (
    get_reader_from_session,
)

from components.ui_helpers import (
    inject_global_css,
    render_login_required,
    render_navbar,
    page_spacer,
    section_title,
    render_stars, render_navigation_section,
)

st.set_page_config(
    page_title="My Posts",
    page_icon="LT",
    layout="wide",
    initial_sidebar_state="collapsed"
)

inject_global_css()

# ========= Login Check =========

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    render_navbar(active_page="discover")
    render_login_required("Please sign in to view your posts.")
    st.stop()

current_reader = get_reader_from_session(st.session_state)

if current_reader is None:
    render_navbar(active_page="discover")
    render_login_required(
        "Cannot load your reader profile. Please log in again.",
        title="Profile unavailable",
        clear_session=True,
    )
    st.stop()

render_navbar(active_page="discover")

page_spacer(20)

section_title("My Posts")

# ========= Get User Posts =========

posts = get_posts_by_reader(current_reader["Reader_ID"])

if not posts:
    st.info("You haven't created any posts yet.")

else:
    for post in posts:

        st.markdown(
            f"""
            <div class="card">
                <h4>{escape(post.get("Title") or "Unknown Book")}</h4>
                <p>{escape(post.get("Content") or "")}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button("Edit", key=f"edit_{post['Post_ID']}"):
                try:
                    st.session_state["edit_post_id"] = post["Post_ID"]
                    st.switch_page("pages/14_Edit_Post.py")
                except Exception as e:
                    st.error("There is an unexpected error: ", e)

        with col2:

            if st.button("Delete", key=f"delete_{post['Post_ID']}"):
                try:
                    delete_post(post["Post_ID"])
                    st.success("Post deleted.")
                    st.rerun()
                except Exception as e:
                    st.error("There is an unexpected error: ", e)

page_spacer(20)
#--------------------------------------------------------------------NAVIGATION
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
section_title("Navigation")
render_navigation_section()