# =============================================================================
# FILE: pages/06_Create_Review.py
# PURPOSE: Dedicated page for writing a book review.
#
# FUTURE BACK-END INTEGRATION:
#   - Submit review: POST /api/reviews
#     Body: { book_id, rating, title, text, visibility, publish_as_post }
#   - If publish_as_post is True: also call POST /api/posts to create a post
#   - The review is linked to book_id in the reviews table
#   - Rating updates the book's avg_rating field (computed in the back-end)
# =============================================================================

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.ui_helpers import (
    inject_global_css, render_navbar, render_book_cover,
    render_stars, page_spacer, section_title, COLORS,
)
from data.mock_data import BOOKS

st.set_page_config(
    page_title="Write a Review — LibTrack",
    page_icon="📖",
    layout="wide",
)
inject_global_css()
render_navbar(active_page="my_library")
page_spacer(30)

_, center_col, _ = st.columns([0.5, 3, 0.5])

with center_col:
    section_title("Write a review")
    st.markdown(
        '<p class="muted">Share your thoughts with the LibTrack community.</p>',
        unsafe_allow_html=True,
    )
    page_spacer(8)

    # -------------------------------------------------------------------------
    # BOOK SELECTOR
    # In production: the selected book_id is included in POST /api/reviews
    # -------------------------------------------------------------------------
    # Pre-select book if navigated from Book Detail page
    default_book_id = st.session_state.get("review_book_id", BOOKS[0]["id"])
    book_options = {f'{b["title"]} — {b["author"]}': b["id"] for b in BOOKS}
    # Find default label
    default_label = next(
        (label for label, bid in book_options.items() if bid == default_book_id),
        list(book_options.keys())[0]
    )

    selected_label = st.selectbox(
        "Select the book you are reviewing",
        options=list(book_options.keys()),
        index=list(book_options.keys()).index(default_label),
        key="cr_book_sel",
    )
    selected_book = next(b for b in BOOKS if b["id"] == book_options[selected_label])

    # Mini book card preview
    mini_col1, mini_col2 = st.columns([0.4, 4])
    with mini_col1:
        st.markdown(render_book_cover(selected_book["cover_color"]), unsafe_allow_html=True)
    with mini_col2:
        st.markdown(
            f'<strong style="color:{COLORS["dark_green"]};">{selected_book["title"]}</strong><br>'
            f'<span class="muted">{selected_book["author"]} · {selected_book["category"]}</span>',
            unsafe_allow_html=True,
        )

    page_spacer(16)
    st.markdown('<hr>', unsafe_allow_html=True)
    page_spacer(8)

    # -------------------------------------------------------------------------
    # STAR RATING
    # In production: stored as `rating` integer (1–5) in the reviews table.
    # Also used to update the book's computed avg_rating field.
    # -------------------------------------------------------------------------
    star_rating = st.select_slider(
        "Your rating",
        options=[1, 2, 3, 4, 5],
        value=4,
        format_func=lambda x: "★" * x + "☆" * (5 - x) + f"  ({x}/5)",
        key="cr_stars",
    )

    page_spacer(8)

    # -------------------------------------------------------------------------
    # REVIEW TITLE
    # In production: stored as `review_title` in the reviews table.
    # -------------------------------------------------------------------------
    review_title = st.text_input(
        "Review title",
        placeholder="Give your review a short title...",
        key="cr_title",
    )

    # -------------------------------------------------------------------------
    # REVIEW TEXT
    # In production: stored as `review_text` (long text) in the reviews table.
    # -------------------------------------------------------------------------
    review_text = st.text_area(
        "Your review",
        placeholder="What did you think? Share your reading experience, what you loved or didn't love, who you'd recommend it to...",
        height=200,
        key="cr_text",
    )

    page_spacer(8)

    vis_col, pub_col = st.columns(2)

    # -------------------------------------------------------------------------
    # VISIBILITY
    # In production: stored as `visibility` enum in the reviews table.
    # 'public' = visible to all, 'followers' = visible to followers only,
    # 'private' = only visible to the author.
    # -------------------------------------------------------------------------
    with vis_col:
        visibility = st.selectbox(
            "Who can see this review?",
            options=["Public", "Followers only", "Private"],
            key="cr_visibility",
        )

    # -------------------------------------------------------------------------
    # PUBLISH AS POST CHECKBOX
    # In production: if True, after POST /api/reviews succeeds, also call
    # POST /api/posts with the review content and book_id, so it appears
    # on followers' feeds.
    # -------------------------------------------------------------------------
    with pub_col:
        page_spacer(28)
        publish_as_post = st.checkbox(
            "Also publish as a community post",
            value=True,
            key="cr_as_post",
            help="If checked, your review will appear in other readers' feeds.",
        )

    page_spacer(16)

    submit_col, cancel_col = st.columns([3, 1])

    with submit_col:
        # In production: POST /api/reviews { ... } then optionally POST /api/posts
        if st.button("Submit review", type="primary", use_container_width=True, key="cr_submit"):
            errors = []
            if not review_text.strip():
                errors.append("Please write your review before submitting.")
            if not review_title.strip():
                errors.append("Please add a short title to your review.")

            if errors:
                for err in errors:
                    st.error(err)
            else:
                msg = "Review published!"
                if publish_as_post:
                    msg += " It has also been shared to the community feed."
                st.success(msg)
                st.balloons()

    with cancel_col:
        if st.button("Cancel", use_container_width=True, key="cr_cancel"):
            st.switch_page("pages/05_Book_Detail.py")