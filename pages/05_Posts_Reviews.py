# =============================================================================
# FILE: pages/05_Posts_Reviews.py
# PURPOSE: Combined page for writing reviews and viewing the activity feed.
#          Matches the "Posts & Reviews" mockup section of LibTrack.
#
# FUTURE BACK-END INTEGRATION:
#   - Activity feed: GET /api/posts?user_id=<id>&following=true
#   - Submit review: POST /api/reviews { book_id, rating, text, visibility }
#   - Like: POST /api/posts/<id>/like
#   - Comment: POST /api/comments { post_id, text }
# =============================================================================

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.ui_helpers import (
    inject_global_css, render_navbar, render_book_cover,
    render_stars, render_badge, render_avatar,
    page_spacer, section_title, COLORS,
)
from data.mock_data import BOOKS, POSTS, CURRENT_USER

st.set_page_config(
    page_title="Posts & Reviews — LibTrack",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed",
)
inject_global_css()
render_navbar(active_page="my_library")
page_spacer(20)

# =============================================================================
# SIDEBAR + MAIN LAYOUT
# =============================================================================
sidebar_col, main_col = st.columns([1, 4])

with sidebar_col:
    if "posts_section" not in st.session_state:
        st.session_state["posts_section"] = "My posts"

    menu_items = ["My profile", "My borrowings", "My posts", "History"]
    for item in menu_items:
        is_active = st.session_state.get("posts_section") == item
        style = (
            f"background:{COLORS['light_green']}; color:{COLORS['dark_green']}; "
            f"border-left:3px solid {COLORS['dark_green']}; font-weight:600;"
        ) if is_active else ""
        if st.button(item, key=f"posts_nav_{item}", use_container_width=True):
            st.session_state["posts_section"] = item
            if item == "My profile":
                st.switch_page("pages/08_Profile.py")
            elif item == "My borrowings":
                st.switch_page("pages/04_Borrowings.py")
            elif item == "History":
                st.switch_page("pages/06_Reading_History.py")
            else:
                st.rerun()

with main_col:
    # =========================================================================
    # WRITE A REVIEW SECTION
    # =========================================================================
    section_title("Write a review")

    # Book selector
    # In production: this book_id is included in POST /api/reviews
    book_options = {f'{b["title"]} — {b["author"]}': b["id"] for b in BOOKS}
    selected_book_label = st.selectbox(
        "Select a book",
        options=list(book_options.keys()),
        key="review_book_sel",
        label_visibility="collapsed",
    )
    selected_book_id = book_options[selected_book_label]
    selected_book = next(b for b in BOOKS if b["id"] == selected_book_id)

    # Show mini book card
    mini_col1, mini_col2 = st.columns([0.4, 4])
    with mini_col1:
        st.markdown(render_book_cover(selected_book["cover_color"]), unsafe_allow_html=True)
    with mini_col2:
        st.markdown(
            f'<strong style="color:{COLORS["dark_green"]};">{selected_book["title"]}</strong><br>'
            f'<span class="muted">{selected_book["author"]}</span>',
            unsafe_allow_html=True,
        )

    page_spacer(8)

    # Star rating selector (1–5)
    # In production: this integer is stored as `rating` in the reviews table.
    review_rating = st.select_slider(
        "Your rating",
        options=[1, 2, 3, 4, 5],
        value=4,
        format_func=lambda x: "★" * x + "☆" * (5 - x),
        key="review_stars",
    )

    # Review text area
    # In production: stored as `review_text` in the reviews table.
    review_text = st.text_area(
        "Your review",
        placeholder="Share your reading experience...",
        height=120,
        label_visibility="collapsed",
        key="review_text_input",
    )

    # Visibility + publish controls
    vis_col, btn_col = st.columns([2, 1])
    with vis_col:
        # In production: stored as `visibility` enum in the reviews table.
        visibility = st.selectbox(
            "Visibility:",
            options=["Public", "Followers only", "Private"],
            key="review_visibility",
            label_visibility="visible",
        )
    with btn_col:
        page_spacer(28)
        # In production: POST /api/reviews { book_id, rating, text, visibility }
        if st.button("Publish", type="primary", key="publish_review", use_container_width=True):
            if review_text.strip():
                st.success("Review published successfully!")
                st.balloons()
            else:
                st.error("Please write something before publishing.")

    page_spacer(16)
    st.markdown('<hr>', unsafe_allow_html=True)

    # =========================================================================
    # ACTIVITY FEED SECTION
    # In production: GET /api/posts?feed=following&user_id=<id>
    # =========================================================================
    section_title("Activity feed")

    for post in POSTS:
        # Action subtitle
        if post["action"] == "rated":
            action_html = f'rated <strong>{post["book_title"]}</strong>'
            rating_html = render_stars(post["rating"])
        elif post["action"] == "borrowed":
            action_html = f'borrowed <strong>{post["book_title"]}</strong>'
            rating_html = ""
        else:
            action_html = f'reviewed <strong>{post["book_title"]}</strong>'
            rating_html = render_stars(post["rating"]) if post.get("rating") else ""

        format_html = render_badge(post["format_tag"], "beige") if post.get("format_tag") else ""

        row_main, row_tag = st.columns([5, 1])
        with row_main:
            st.markdown(
                f"""
                <div class="card">
                    <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
                        {render_avatar(post['initials'], post['avatar_color'], post['text_color'])}
                        <div style="flex:1;">
                            <strong>{post['user']}</strong>
                            <span class="muted"> {action_html} · {post['time_ago']}</span>
                        </div>
                        <div>{rating_html}</div>
                    </div>
                    <p style="font-size:0.92rem; line-height:1.55; margin:6px 0 10px 0;">
                        {post['content']}
                    </p>
                    <span class="action-row">♡ {post['likes']} likes &nbsp; 💬 {post['comments']} comments</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with row_tag:
            page_spacer(10)
            if format_html:
                st.markdown(format_html, unsafe_allow_html=True)
            page_spacer(4)
            # In production: POST /api/posts/<id>/like
            if st.button("♡", key=f"like_pr_{post['id']}"):
                st.toast(f"Liked!")
            # In production: opens comment input
            if st.button("💬", key=f"cmt_pr_{post['id']}"):
                st.toast("Comments coming soon!")