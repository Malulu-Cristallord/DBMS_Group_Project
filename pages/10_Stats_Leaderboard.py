# =============================================================================
# FILE: pages/10_Stats_Leaderboard.py
# PURPOSE: Platform-wide statistics, leaderboard, and user badges/rewards.
#
# FUTURE BACK-END INTEGRATION:
#   - Platform stats: GET /api/stats/platform
#   - Most borrowed: GET /api/books?sort=borrowings&limit=10
#   - Leaderboard: GET /api/leaderboard?period=month
#   - User badges: GET /api/rewards?user_id=<id>
#   - Badge progress: GET /api/rewards/progress?user_id=<id>
# =============================================================================

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.ui_helpers import (
    inject_global_css, render_navbar, render_book_cover,
    render_stars, render_badge, render_avatar, render_progress_bar,
    render_stat_card, page_spacer, section_title, COLORS,
)
from data.mock_data import (
    PLATFORM_STATS, MOST_BORROWED, LEADERBOARD,
    ALL_BADGES, CURRENT_USER,
)

st.set_page_config(
    page_title="Stats & Leaderboard — LibTrack",
    page_icon="📖",
    layout="wide",
)
inject_global_css()
render_navbar(active_page="discover")
page_spacer(24)

# =============================================================================
# PLATFORM STATISTICS CARDS
# In production: GET /api/stats/platform
# =============================================================================
stat_cols = st.columns(4)

stats_items = [
    (f'{PLATFORM_STATS["active_readers"]:,}', "Active readers"),
    (f'{PLATFORM_STATS["borrowings_this_month"]:,}', "Borrowings this month"),
    (f'{PLATFORM_STATS["reviews_published"]:,}', "Reviews published"),
    (str(PLATFORM_STATS["available_titles"]), "Available titles"),
]

for i, (num, label) in enumerate(stats_items):
    with stat_cols[i]:
        st.markdown(render_stat_card(num, label), unsafe_allow_html=True)

page_spacer(30)

# =============================================================================
# TWO-COLUMN LAYOUT: Most borrowed + Leaderboard & Badges
# =============================================================================
left_col, right_col = st.columns([3, 2])

# =============================================================================
# LEFT — Most borrowed books
# In production: GET /api/books?sort=borrowings&period=month&limit=10
# =============================================================================
with left_col:
    section_title("Most borrowed books")

    for book in MOST_BORROWED:
        rank_col, cover_col, info_col, stars_col = st.columns([0.3, 0.6, 4, 1.5])

        with rank_col:
            page_spacer(12)
            st.markdown(
                f'<span style="font-family: \'Playfair Display\', Georgia, serif; '
                f'font-size:1.3rem; font-weight:700; color:{COLORS["text_muted"]};">'
                f'{book["rank"]}</span>',
                unsafe_allow_html=True,
            )

        with cover_col:
            page_spacer(6)
            st.markdown(render_book_cover(book["cover_color"]), unsafe_allow_html=True)

        with info_col:
            st.markdown(
                f'<strong style="font-size:0.95rem; color:{COLORS["dark_green"]};">'
                f'{book["title"]}</strong><br>'
                f'<span class="muted">{book["author"]} · {book["borrowings"]} borrowings</span>',
                unsafe_allow_html=True,
            )

        with stars_col:
            page_spacer(12)
            st.markdown(
                f'<span class="muted" style="font-size:0.8rem;">★★★★★</span>',
                unsafe_allow_html=True,
            )

        st.markdown('<hr>', unsafe_allow_html=True)

# =============================================================================
# RIGHT — Leaderboard + User Badges
# =============================================================================
with right_col:

    # -------------------------------------------------------------------------
    # LEADERBOARD
    # In production: GET /api/leaderboard?period=month&limit=10
    # -------------------------------------------------------------------------
    section_title("Most active readers")

    for reader in LEADERBOARD:
        r_col, av_col, info_col, badge_col = st.columns([0.3, 0.6, 2.5, 0.8])

        with r_col:
            page_spacer(12)
            st.markdown(
                f'<span style="font-weight:700; color:{COLORS["text_muted"]}; font-size:1rem;">'
                f'{reader["rank"]}</span>',
                unsafe_allow_html=True,
            )

        with av_col:
            page_spacer(8)
            st.markdown(
                render_avatar(reader["initials"], reader["avatar_color"], reader["text_color"]),
                unsafe_allow_html=True,
            )

        with info_col:
            you_label = ' <span class="muted">(you)</span>' if reader["is_current_user"] else ""
            st.markdown(
                f'<strong style="font-size:0.9rem; color:{COLORS["dark_green"]};">'
                f'{reader["user"]}{you_label}</strong><br>'
                f'<span class="muted">{reader["books_this_month"]} books this month</span>',
                unsafe_allow_html=True,
            )

        with badge_col:
            page_spacer(12)
            if reader.get("badge"):
                badge_style = "gold" if reader["badge"] == "Gold" else "grey"
                st.markdown(render_badge(reader["badge"], badge_style), unsafe_allow_html=True)

    page_spacer(20)
    st.markdown('<hr>', unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # USER BADGES
    # In production: GET /api/rewards?user_id=<id>
    # Shows earned badges and progress toward locked ones.
    # -------------------------------------------------------------------------
    section_title("Your badges")

    # Earned badges
    earned_badges = [b for b in ALL_BADGES if b["earned"]]
    badges_html = ""
    for badge in earned_badges:
        style = "gold" if "reviewer" in badge["name"].lower() or "gold" in badge["name"].lower() else "green"
        badges_html += render_badge(badge["name"], style) + " "
    st.markdown(badges_html + "<br>", unsafe_allow_html=True)

    page_spacer(10)

    # Locked badges with progress
    locked_badges = [b for b in ALL_BADGES if not b["earned"]]
    if locked_badges:
        st.markdown('<p class="muted" style="font-size:0.85rem;">Progress toward next badges:</p>', unsafe_allow_html=True)
        for badge in locked_badges:
            st.markdown(
                f'<span class="muted" style="font-size:0.82rem;">{badge["name"]} — {badge["description"]}</span>',
                unsafe_allow_html=True,
            )
            st.markdown(render_progress_bar(badge["progress"]), unsafe_allow_html=True)
            st.markdown(
                f'<span class="muted" style="font-size:0.75rem;">{badge["progress"]}%</span>',
                unsafe_allow_html=True,
            )
            page_spacer(6)