# =============================================================================
# FILE: pages/07_Create_Post.py
# PURPOSE: Allows the user to create a new community post.
#
# FUTURE BACK-END INTEGRATION:
#   - Submit post: POST /api/posts { content, book_id, milestone, visibility }
#   - book_id links the post to a specific book in the books table
#   - visibility controls who can see the post
# =============================================================================

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.ui_helpers import (
    inject_global_css, render_navbar, render_avatar,
    page_spacer, section_title, COLORS,
)
from data.mock_data import BOOKS, CURRENT_USER

st.set_page_config(
    page_title="Create Post — LibTrack",
    page_icon="📖",
    layout="wide",
)
inject_global_css()
render_navbar(active_page="my_library")
page_spacer(30)

_, center_col, _ = st.columns([1, 2.5, 1])

with center_col:
    section_title("Create a post")

    # Show user avatar and name
    st.markdown(
        f'<div style="display:flex; align-items:center; gap:12px; margin-bottom:20px;">'
        f'{render_avatar(CURRENT_USER["initials"], COLORS["gold"], COLORS["brown"], "normal")}'
        f'<strong style="font-size:1rem; color:{COLORS["dark_green"]};">'
        f'{CURRENT_USER["username"]}</strong>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # -------------------------------------------------------------------------
    # POST CONTENT TEXT AREA
    # In production: sent as `content` to POST /api/posts
    # -------------------------------------------------------------------------
    post_content = st.text_area(
        "What's on your mind?",
        placeholder="Share your reading thoughts, a quote, a milestone, or a recommendation...",
        height=160,
        key="post_content",
        label_visibility="collapsed",
    )

    page_spacer(8)

    # -------------------------------------------------------------------------
    # OPTIONAL BOOK SELECTOR
    # In production: the selected book_id is included in POST /api/posts
    # to link this post to a specific book in the database.
    # -------------------------------------------------------------------------
    book_options = {"No book linked": None}
    book_options.update({f'{b["title"]} — {b["author"]}': b["id"] for b in BOOKS})

    linked_book = st.selectbox(
        "Link to a book (optional)",
        options=list(book_options.keys()),
        key="post_book",
        help="Link your post to a book so other readers can find it on the book page.",
    )

    # -------------------------------------------------------------------------
    # OPTIONAL READING MILESTONE SELECTOR
    # In production: stored as a `milestone_type` enum in the posts table.
    # Milestones can trigger badge awards in the reward system.
    # -------------------------------------------------------------------------
    milestone_options = [
        "No milestone",
        "Started a new book",
        "Finished a book",
        "Read 5 books this month",
        "Reached a reading streak",
        "Personal record",
    ]
    milestone = st.selectbox(
        "Reading milestone (optional)",
        options=milestone_options,
        key="post_milestone",
        help="Share a reading achievement to inspire the community!",
    )

    page_spacer(4)

    # -------------------------------------------------------------------------
    # VISIBILITY SELECTOR
    # In production: stored as `visibility` enum ('public', 'followers', 'private')
    # in the posts table. Controls who can see this post.
    # -------------------------------------------------------------------------
    visibility = st.selectbox(
        "Visibility",
        options=["Public", "Followers only", "Private"],
        key="post_visibility",
        help="Public posts are visible to all readers on the platform.",
    )

    page_spacer(12)

    publish_col, cancel_col = st.columns([3, 1])

    with publish_col:
        # In production: sends POST /api/posts and redirects to the feed
        if st.button("Publish post", type="primary", use_container_width=True, key="pub_post"):
            if post_content.strip():
                st.success("Your post has been published to the community feed!")
                st.balloons()
            else:
                st.error("Please write something before publishing.")

    with cancel_col:
        # In production: navigates back without saving
        if st.button("Cancel", use_container_width=True, key="cancel_post"):
            st.switch_page("app.py")