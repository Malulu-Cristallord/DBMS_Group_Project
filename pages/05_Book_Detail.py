# =============================================================================
# FILE: pages/05_Book_Detail.py
# PURPOSE: Detailed view of a single book.
#          Shows title, author, description, availability, reviews, and actions.
#
# FUTURE BACK-END INTEGRATION:
#   - Book data: GET /api/books/<book_id>
#   - Reviews: GET /api/reviews?book_id=<book_id>
#   - Borrow: POST /api/borrowings { book_id, format }
#   - Reserve: POST /api/reservations { book_id }
#   - Wishlist: POST /api/wishlist { book_id }
#   - External purchase: redirect to book.purchase_url
# =============================================================================

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.ui_helpers import (
    inject_global_css, render_navbar, render_book_cover,
    render_stars, render_badge, render_avatar, render_progress_bar,
    page_spacer, section_title, COLORS,
)
from data.mock_data import BOOKS, REVIEWS

st.set_page_config(
    page_title="Book Detail — LibTrack",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed",
)
inject_global_css()
render_navbar(active_page="discover")
page_spacer(20)

# =============================================================================
# DETERMINE WHICH BOOK TO SHOW
# In production: the book_id comes from the URL parameter (/books/<book_id>)
# =============================================================================
book_id = st.session_state.get("selected_book_id", "book_001")
book = next((b for b in BOOKS if b["id"] == book_id), BOOKS[0])

# Get reviews for this book
book_reviews = [r for r in REVIEWS if r["book_id"] == book["id"]]

# =============================================================================
# BACK NAVIGATION
# =============================================================================
if st.button("← Back to Discovery"):
    st.switch_page("pages/03_Discovery.py")

page_spacer(10)

# =============================================================================
# BOOK HEADER SECTION
# =============================================================================
main_col, avail_col = st.columns([3, 1])

with main_col:
    header_cols = st.columns([1, 4])

    with header_cols[0]:
        st.markdown(render_book_cover(book["cover_color"], "large"), unsafe_allow_html=True)

    with header_cols[1]:
        # Book title and metadata
        st.markdown(
            f'<h1 style="font-size:2rem; margin-bottom:4px;">{book["title"]}</h1>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<p class="secondary" style="font-size:1rem; margin-bottom:10px;">'
            f'{book["author"]} · {book["category"]} · {book["year"]}</p>',
            unsafe_allow_html=True,
        )

        # Rating and review count
        st.markdown(
            f'{render_stars(book["avg_rating"])} '
            f'<span class="muted">· {book["review_count"]} reviews</span>',
            unsafe_allow_html=True,
        )

        page_spacer(10)

        # Availability and format badges
        physical_avail = book.get("physical_available", "—")
        is_available = physical_avail not in ["0 / 2", "0 / 3"]

        badges_html = (render_badge("Available", "available") if is_available
                       else render_badge("Waitlist", "waitlist"))
        if "Physical" in book["formats"]:
            badges_html += " " + render_badge("Physical", "beige")
        if "E-book" in book["formats"]:
            badges_html += " " + render_badge("E-book", "grey")
        st.markdown(badges_html, unsafe_allow_html=True)

        page_spacer(14)

        # Action buttons row
        btn_cols = st.columns(3)
        with btn_cols[0]:
            # In production: POST /api/borrowings { book_id, format: "physical" }
            if st.button("📚 Borrow (physical)", type="primary", key="borrow_phys"):
                if is_available:
                    st.toast("Physical copy borrowed successfully!")
                else:
                    st.toast("No physical copies available — added to reserve queue.")

        with btn_cols[1]:
            # In production: POST /api/borrowings { book_id, format: "ebook" }
            if st.button("📱 Borrow (e-book)", key="borrow_ebook"):
                if book.get("ebook_available"):
                    st.toast("E-book borrowed successfully! Open in your reader.")
                else:
                    st.toast("E-book not available for this title.")

        with btn_cols[2]:
            # In production: POST /api/wishlist { book_id }
            if st.button("+ Wishlist", key="wishlist_btn"):
                st.toast(f"'{book['title']}' added to your wishlist!")

# =============================================================================
# RIGHT PANEL — Availability details
# =============================================================================
with avail_col:
    st.markdown(
        f'<div class="card">'
        f'<p style="font-size:0.8rem; font-weight:600; color:{COLORS["text_muted"]}; '
        f'text-transform:uppercase; letter-spacing:0.08em; margin-bottom:12px;">Availability</p>',
        unsafe_allow_html=True,
    )

    if "Physical" in book["formats"]:
        physical_parts = book["physical_available"].split(" / ")
        current = int(physical_parts[0])
        total = int(physical_parts[1])
        pct = int((current / total) * 100) if total > 0 else 0

        st.markdown(
            f'<p class="secondary" style="margin-bottom:4px;">Physical copies</p>'
            f'<strong style="font-size:1rem;">{book["physical_available"]} available</strong>',
            unsafe_allow_html=True,
        )
        st.markdown(render_progress_bar(pct), unsafe_allow_html=True)

    if book.get("ebook_available"):
        page_spacer(10)
        st.markdown(
            f'<p class="secondary" style="margin-bottom:4px;">E-book</p>'
            f'{render_badge("Always available", "available")}',
            unsafe_allow_html=True,
        )

    page_spacer(16)

    # In production: redirects to book.purchase_url (external bookstore)
    if st.button("🛒 Buy this book", key="purchase_btn", use_container_width=True):
        st.markdown(
            f'<a href="{book["purchase_url"]}" target="_blank">Opening store...</a>',
            unsafe_allow_html=True,
        )
        st.info("Redirecting to external bookstore...")

    st.markdown('</div>', unsafe_allow_html=True)

page_spacer(20)
st.markdown('<hr>', unsafe_allow_html=True)

# =============================================================================
# BOOK DESCRIPTION
# =============================================================================
st.markdown(
    f'<p style="font-size:0.97rem; line-height:1.7; max-width:720px; '
    f'color:{COLORS["text_secondary"]};">{book["description"]}</p>',
    unsafe_allow_html=True,
)

page_spacer(20)
st.markdown('<hr>', unsafe_allow_html=True)

# =============================================================================
# WRITE A REVIEW BUTTON
# In production: navigates to /reviews/create?book_id=<book_id>
# =============================================================================
section_title("Share your thoughts")
if st.button("✏️ Write a review for this book", type="primary", key="write_review_btn"):
    st.session_state["review_book_id"] = book["id"]
    st.switch_page("pages/06_Create_Review.py")

page_spacer(20)
st.markdown('<hr>', unsafe_allow_html=True)

# =============================================================================
# COMMUNITY REVIEWS SECTION
# In production: GET /api/reviews?book_id=<book_id>&sort=recent
# =============================================================================
section_title("Community reviews")

if book_reviews:
    for review in book_reviews:
        st.markdown(
            f"""
            <div class="card">
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
                    {render_avatar(review['initials'], review['avatar_color'], review['text_color'])}
                    <div style="flex:1;">
                        <strong>{review['user']}</strong>
                        {render_stars(review['rating'])}
                    </div>
                    <span class="muted">{review['time_ago']}</span>
                </div>
                <p style="font-size:0.93rem; line-height:1.6; margin:0;">{review['text']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.markdown(
        '<p class="muted">No reviews yet. Be the first to share your thoughts!</p>',
        unsafe_allow_html=True,
    )