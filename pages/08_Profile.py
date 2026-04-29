# =============================================================================
# FILE: pages/08_Profile.py
# PURPOSE: User profile page — shows stats, badges, wishlist, and posts.
#
# FUTURE BACK-END INTEGRATION:
#   - Profile data: GET /api/users/<user_id>/profile
#   - Posts: GET /api/posts?user_id=<id>
#   - Wishlist: GET /api/wishlist?user_id=<id>
#   - Badges: GET /api/rewards?user_id=<id>
#   - Edit profile: PUT /api/users/<user_id>/profile
#   - Privacy settings: PUT /api/users/<user_id>/privacy
# =============================================================================

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.ui_helpers import (
    inject_global_css, render_navbar, render_book_cover,
    render_stars, render_badge, render_avatar, render_progress_bar,
    page_spacer, section_title, COLORS,
)
from data.mock_data import CURRENT_USER, POSTS, WISHLIST, ALL_BADGES

st.set_page_config(
    page_title="Profile — LibTrack",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed",
)
inject_global_css()
render_navbar(active_page="my_library")
page_spacer(20)

# =============================================================================
# LAYOUT: sidebar + profile center + latest posts
# =============================================================================
sidebar_col, profile_col, posts_col = st.columns([1, 3, 1.8])

# =============================================================================
# SIDEBAR NAVIGATION
# =============================================================================
with sidebar_col:
    menu_items = ["My profile", "My borrowings", "My posts", "History", "Settings"]
    for item in menu_items:
        is_active = item == "My profile"
        if st.button(item, key=f"prof_nav_{item}", use_container_width=True):
            if item == "My borrowings":
                st.switch_page("pages/04_Borrowings.py")
            elif item == "My posts":
                st.switch_page("pages/05_Posts_Reviews.py")
            elif item == "History":
                st.switch_page("pages/06_Reading_History.py")
            elif item == "Settings":
                st.switch_page("pages/09_Settings.py")

# =============================================================================
# PROFILE CENTER
# =============================================================================
with profile_col:
    # --- USER AVATAR + NAME + BADGES ---
    avatar_col, info_col, edit_col = st.columns([0.8, 3, 1.2])

    with avatar_col:
        st.markdown(
            render_avatar(CURRENT_USER["initials"], COLORS["gold"], COLORS["brown"], "large"),
            unsafe_allow_html=True,
        )

    with info_col:
        st.markdown(
            f'<h2 style="margin-bottom:2px;">{CURRENT_USER["username"]}</h2>'
            f'<span class="muted">Member since {CURRENT_USER["member_since"]}</span><br>',
            unsafe_allow_html=True,
        )
        # Show user badges
        earned = [b for b in ALL_BADGES if b["earned"]][:2]
        badges_html = ""
        for badge in earned:
            style = "green" if "reader" in badge["name"].lower() else "gold"
            badges_html += render_badge(badge["name"], style) + " "
        st.markdown(badges_html, unsafe_allow_html=True)

    with edit_col:
        page_spacer(10)
        # In production: navigate to edit profile form / PUT /api/users/<id>/profile
        if st.button("Edit profile", key="edit_prof_btn"):
            st.switch_page("pages/09_Settings.py")

    page_spacer(16)
    st.markdown('<hr>', unsafe_allow_html=True)

    # --- STATISTICS ROW ---
    stats = [
        (str(CURRENT_USER["books_borrowed"]), "Books borrowed"),
        (str(CURRENT_USER["posts_published"]), "Posts published"),
        (str(CURRENT_USER["avg_rating"]), "Avg. rating"),
        (str(CURRENT_USER["followers"]), "Followers"),
    ]

    stat_cols = st.columns(4)
    for i, (val, label) in enumerate(stats):
        with stat_cols[i]:
            st.markdown(
                f'<div style="text-align:center;">'
                f'<div style="font-family: \'Playfair Display\', Georgia, serif; '
                f'font-size:1.6rem; font-weight:700; color:{COLORS["dark_green"]};">{val}</div>'
                f'<div class="muted" style="font-size:0.78rem;">{label}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    page_spacer(20)
    st.markdown('<hr>', unsafe_allow_html=True)

    # --- PRIVACY SETTINGS ---
    section_title("Privacy settings")

    # In production: each toggle calls PUT /api/users/<id>/privacy
    make_public = st.toggle(
        "Make my borrowings public",
        value=CURRENT_USER["show_borrowings"],
        key="priv_borrowings",
    )
    show_history = st.toggle(
        "Show my reading history",
        value=CURRENT_USER.get("show_reading_history", True),
        key="priv_history",
    )
    receive_recs = st.toggle(
        "Receive recommendations",
        value=CURRENT_USER["receive_recommendations"],
        key="priv_recs",
    )

    if st.button("Save privacy settings", type="primary", key="save_priv"):
        st.success("Privacy settings saved!")

    page_spacer(20)
    st.markdown('<hr>', unsafe_allow_html=True)

    # --- BIO ---
    section_title("About")
    st.markdown(
        f'<p style="font-size:0.93rem; color:{COLORS["text_secondary"]}; line-height:1.6;">'
        f'{CURRENT_USER["bio"]}</p>',
        unsafe_allow_html=True,
    )

    # Preferred genres
    st.markdown('<p class="muted" style="margin-top:10px;">Preferred genres:</p>', unsafe_allow_html=True)
    genres_html = ""
    for g in CURRENT_USER["preferred_genres"]:
        genres_html += render_badge(g, "green") + " "
    st.markdown(genres_html, unsafe_allow_html=True)

    page_spacer(20)
    st.markdown('<hr>', unsafe_allow_html=True)

    # --- WISHLIST ---
    section_title("My wishlist")
    if WISHLIST:
        for item in WISHLIST:
            w_col1, w_col2 = st.columns([0.5, 4])
            with w_col1:
                st.markdown(render_book_cover(item["cover_color"]), unsafe_allow_html=True)
            with w_col2:
                st.markdown(
                    f'<strong style="color:{COLORS["dark_green"]};">{item["title"]}</strong><br>'
                    f'<span class="muted">{item["author"]}</span>',
                    unsafe_allow_html=True,
                )
    else:
        st.markdown('<p class="muted">Your wishlist is empty.</p>', unsafe_allow_html=True)

# =============================================================================
# RIGHT PANEL — Latest posts
# In production: GET /api/posts?user_id=<id>&limit=5
# =============================================================================
with posts_col:
    section_title("Latest posts")

    user_posts = [p for p in POSTS if p["user"] == CURRENT_USER["username"]]
    # If no exact match, show some posts as demo
    if not user_posts:
        user_posts = POSTS[:2]

    for post in user_posts[:3]:
        # Find book for this post
        book = next((b for b in __import__('data.mock_data', fromlist=['BOOKS']).BOOKS
                     if b["id"] == post.get("book_id")), None)
        cover_color = book["cover_color"] if book else COLORS["mid_green"]

        col_cover, col_text = st.columns([0.5, 2.5])
        with col_cover:
            st.markdown(render_book_cover(cover_color), unsafe_allow_html=True)
        with col_text:
            st.markdown(
                f'<strong class="secondary">{post["book_title"]}</strong><br>'
                f'<span class="muted" style="font-size:0.82rem;">'
                f'"{post["content"][:60]}..."</span>',
                unsafe_allow_html=True,
            )
        page_spacer(10)