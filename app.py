# =============================================================================
# FILE: app.py
# PURPOSE: Main entry point for the LibTrack Streamlit application.
#          This file configures the app-wide settings and serves as the
#          landing/home feed page.
#
# HOW TO RUN:
#   streamlit run app.py
#
# NOTE: This is a FRONT-END ONLY project using mock data.
#       No real database or back-end exists yet.
#       All data comes from data/mock_data.py
# =============================================================================

import streamlit as st
import sys
import os

# Add the project root to the Python path so we can import our modules
sys.path.insert(0, os.path.dirname(__file__))

from components.ui_helpers import (
    inject_global_css,
    render_navbar,
    render_book_cover,
    render_stars,
    render_badge,
    render_avatar,
    page_spacer,
    section_title,
    COLORS,
)
from data.mock_data import (
    CURRENT_USER,
    BOOKS,
    POSTS,
)


# =============================================================================
# PAGE CONFIGURATION
# Must be the FIRST Streamlit command in every file.
# =============================================================================
st.set_page_config(
    page_title="LibTrack — Your Reading Journey",
    page_icon="📖",
    layout="wide"
)

# Inject global CSS for consistent design
inject_global_css()

# =============================================================================
# TOP NAVIGATION BAR
# =============================================================================
render_navbar(active_page="discover")

page_spacer(24)

# =============================================================================
# WELCOME HEADER
# =============================================================================
col_welcome, col_action = st.columns([3, 1])
with col_welcome:
    st.markdown(
        f'<h1 style="margin-bottom:4px;">Welcome back, {CURRENT_USER["username"].split()[0]} 👋</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="secondary">Discover your next great read and share your journey.</p>',
        unsafe_allow_html=True,
    )

with col_action:
    page_spacer(10)
    # In production: this button routes to the Create Post page.
    if st.button("✏️ Create a post", type="primary", use_container_width=True):
        st.switch_page("pages/07_Create_Post.py")

page_spacer(10)

# =============================================================================
# QUICK SEARCH BAR
# In production: this value is sent to GET /api/books?search=<query>
# =============================================================================
search_query = st.text_input(
    "",
    placeholder="🔍  Search for a book, author, or genre...",
    label_visibility="collapsed",
    key="home_search",
)

if search_query:
    # In production: redirect to the book discovery page with the query pre-filled.
    st.info(f"Searching for: **{search_query}** — go to the Book Discovery page for full results.")

page_spacer(20)
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# =============================================================================
# RECOMMENDED BOOKS SECTION
# In production: books come from GET /api/recommendations?user_id=<id>
# =============================================================================
section_title("📚 Recommended for you")

# Filter to show books matching user's preferred genres
recommended = [
    b for b in BOOKS
    if b["category"] in CURRENT_USER["preferred_genres"]
][:4]

rec_cols = st.columns(4)
for i, book in enumerate(recommended):
    with rec_cols[i]:
        st.markdown(render_book_cover(book["cover_color"], size="card"), unsafe_allow_html=True)
        st.markdown(
            f'<strong style="font-size:0.9rem; color:{COLORS["dark_green"]};">{book["title"]}</strong>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<span class="muted">{book["author"]}</span><br>'
            f'{render_stars(book["avg_rating"])}',
            unsafe_allow_html=True,
        )
        # In production: this navigates to /books/<book_id>
        if st.button("View", key=f"rec_{book['id']}", use_container_width=True):
            st.session_state["selected_book_id"] = book["id"]
            st.switch_page("pages/05_Book_Detail.py")

page_spacer(20)
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

if st.button("Find books", type="primary"):
    st.switch_page("pages/03_Discovery.py")

# =============================================================================
# POPULAR BOOKS OF THE WEEK
# In production: books come from GET /api/books/popular?period=week
# =============================================================================
section_title("🔥 Popular this week")

popular = [b for b in BOOKS if b.get("popular")][:6]

pop_cols = st.columns(6)
for i, book in enumerate(popular):
    with pop_cols[i]:
        st.markdown(render_book_cover(book["cover_color"], size="card"), unsafe_allow_html=True)
        st.markdown(
            f'<span style="font-size:0.8rem; font-weight:600; color:{COLORS["dark_green"]};">'
            f'{book["title"]}</span><br>'
            f'<span class="muted" style="font-size:0.75rem;">{book["author"]}</span>',
            unsafe_allow_html=True,
        )

page_spacer(20)
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# =============================================================================
# COMMUNITY FEED
# In production: posts come from GET /api/posts?feed=home&user_id=<id>
# =============================================================================
section_title("🌿 Activity feed")

for post in POSTS:
    # Build the sub-heading line depending on action type
    if post["action"] == "rated":
        action_html = f'rated <strong>{post["book_title"]}</strong>'
    elif post["action"] == "borrowed":
        action_html = f'borrowed <strong>{post["book_title"]}</strong>'
    else:
        action_html = f'reviewed <strong>{post["book_title"]}</strong>'

    # Optional: show star rating if review
    rating_html = ""
    if post.get("rating"):
        rating_html = render_stars(post["rating"])

    # Optional: format tag (Physical / E-book)
    format_html = ""
    if post.get("format_tag"):
        format_html = render_badge(post["format_tag"], style="beige")

    col_post, col_tag = st.columns([5, 1])
    with col_post:
        st.markdown(
            f"""
            <div class="card">
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
                    {render_avatar(post['initials'], post['avatar_color'], post['text_color'])}
                    <div>
                        <strong style="font-size:0.95rem;">{post['user']}</strong>
                        <span class="muted"> {action_html} · {post['time_ago']}</span>
                    </div>
                    <div style="margin-left:auto;">{rating_html}</div>
                </div>
                <p style="margin:6px 0 10px 0; font-size:0.92rem; line-height:1.55;">{post['content']}</p>
                <div class="action-row">
                    ♡ {post['likes']} likes &nbsp;&nbsp; 💬 {post['comments']} comments
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_tag:
        page_spacer(8)
        if post.get("format_tag"):
            st.markdown(format_html, unsafe_allow_html=True)

        # In production: LIKE sends POST /api/posts/<post_id>/like
        if st.button(f"♡ Like", key=f"like_{post['id']}"):
            st.toast(f"Liked post by {post['user']}!")

        # In production: COMMENT opens comments panel or sends POST /api/comments
        if st.button(f"💬 Comment", key=f"comment_{post['id']}"):
            st.toast("Comments coming soon!")

page_spacer(20)