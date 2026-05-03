from html import escape
import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Backend.Functions.library_data import (
    get_books,
    get_leaderboard,
    get_platform_stats,
    get_reader_badges,
    get_reader_from_session,
)
from components.ui_helpers import (
    COLORS,
    inject_global_css,
    page_spacer,
    render_avatar,
    render_badge,
    render_book_cover,
    render_progress_bar,
    render_navbar,
    render_stat_card,
    render_stars,
    section_title,
)


st.set_page_config(
    page_title="Stats & Leaderboard | LibTrack",
    page_icon="LT",
    layout="wide",
)

inject_global_css()
render_navbar(active_page="discover")
page_spacer(24)


current_reader = get_reader_from_session(st.session_state)
platform_stats = get_platform_stats()

stat_cols = st.columns(4)

stats_items = [
    (f'{platform_stats["active_readers"]:,}', "Active readers"),
    (f'{platform_stats["borrowings_this_month"]:,}', "Borrowings this month"),
    (f'{platform_stats["reviews_published"]:,}', "Posts published"),
    (str(platform_stats["available_titles"]), "Available titles"),
]

for index, (number, label) in enumerate(stats_items):
    with stat_cols[index]:
        st.markdown(render_stat_card(number, label), unsafe_allow_html=True)

page_spacer(30)

left_col, right_col = st.columns([3, 2])

with left_col:
    section_title("Top rated books")

    books = get_books(sort_option="rating", limit=10)
    if not books:
        st.info("No books are available in the database yet.")

    for rank, book in enumerate(books, start=1):
        rank_col, cover_col, info_col, stars_col = st.columns([0.3, 0.6, 4, 1.5])

        with rank_col:
            page_spacer(12)
            st.markdown(
                f'<span style="font-size:1.3rem; font-weight:700; color:{COLORS["text_muted"]};">'
                f'{rank}</span>',
                unsafe_allow_html=True,
            )

        with cover_col:
            page_spacer(6)
            st.markdown(render_book_cover(book["cover"]), unsafe_allow_html=True)

        with info_col:
            st.markdown(
                f'<strong style="font-size:0.95rem; color:{COLORS["dark_green"]};">'
                f'{escape(book["title"])}</strong><br>'
                f'<span class="muted">{escape(book["author"])} - {book["review_count"]} posts</span>',
                unsafe_allow_html=True,
            )

        with stars_col:
            page_spacer(12)
            st.markdown(render_stars(book["avg_rating"]), unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)


with right_col:
    section_title("Most active readers")

    leaderboard = get_leaderboard(
        current_reader_id=current_reader["Reader_ID"] if current_reader else None,
        limit=10,
    )
    if not leaderboard:
        st.info("No readers are available in the database yet.")

    for reader in leaderboard:
        rank_col, avatar_col, info_col, badge_col = st.columns([0.3, 0.6, 2.5, 0.8])

        with rank_col:
            page_spacer(12)
            st.markdown(
                f'<span style="font-weight:700; color:{COLORS["text_muted"]}; font-size:1rem;">'
                f'{reader["rank"]}</span>',
                unsafe_allow_html=True,
            )

        with avatar_col:
            page_spacer(8)
            st.markdown(
                render_avatar(reader["initials"], COLORS["light_green"], COLORS["dark_green"]),
                unsafe_allow_html=True,
            )

        with info_col:
            you_label = ' <span class="muted">(you)</span>' if reader["is_current_reader"] else ""
            st.markdown(
                f'<strong style="font-size:0.9rem; color:{COLORS["dark_green"]};">'
                f'{escape(reader["reader_name"])}{you_label}</strong><br>'
                f'<span class="muted">{reader["points"]} reader points</span>',
                unsafe_allow_html=True,
            )

        with badge_col:
            page_spacer(12)
            if reader.get("badge"):
                badge_style = "gold" if reader["badge"] == "Gold" else "grey"
                st.markdown(render_badge(reader["badge"], badge_style), unsafe_allow_html=True)

    page_spacer(20)
    st.markdown("<hr>", unsafe_allow_html=True)

    section_title("Your badges")

    if current_reader is None:
        st.info("Sign in to view reader badge progress.")
    else:
        badges = get_reader_badges(current_reader)
        earned_badges = [badge for badge in badges if badge["earned"]]

        if earned_badges:
            st.markdown(
                " ".join(render_badge(badge["name"], "green") for badge in earned_badges),
                unsafe_allow_html=True,
            )
        else:
            st.markdown('<p class="muted">No badges earned yet.</p>', unsafe_allow_html=True)

        page_spacer(10)

        locked_badges = [badge for badge in badges if not badge["earned"]]
        for badge in locked_badges:
            st.markdown(
                f'<span class="muted" style="font-size:0.82rem;">'
                f'{escape(badge["name"])} - {escape(badge["description"])}</span>',
                unsafe_allow_html=True,
            )
            st.markdown(render_progress_bar(badge["progress"]), unsafe_allow_html=True)
            page_spacer(6)
