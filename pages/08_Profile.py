from html import escape
import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Backend.Functions.library_data import (
    get_reader_badges,
    get_reader_from_session,
    get_reader_genres,
    get_reader_stats,
    get_posts,
    reader_initials,
    update_reader_profile,
)
from components.ui_helpers import (
    COLORS,
    inject_global_css,
    page_spacer,
    render_avatar,
    render_badge,
    render_progress_bar,
    render_navbar,
    section_title,
)


st.set_page_config(
    page_title="Profile | LibTrack",
    page_icon="LT",
    layout="wide",
)

inject_global_css()
render_navbar(active_page="my_library")
page_spacer(20)


current_reader = get_reader_from_session(st.session_state)
if current_reader is None:
    st.warning("Please sign in to view your reader profile.")
    if st.button("Go to Login", type="primary"):
        st.switch_page("pages/01_Login.py")
    st.stop()


reader_stats = get_reader_stats(current_reader["Reader_ID"])
reader_posts = get_posts(reader_id=current_reader["Reader_ID"], limit=5)
reader_badges = get_reader_badges(current_reader, reader_stats["posts_published"])


sidebar_col, profile_col, posts_col = st.columns([1, 3, 1.8])

with sidebar_col:
    menu_items = ["My profile", "My borrowings", "My posts", "History", "Settings"]
    for item in menu_items:
        if st.button(item, key=f"prof_nav_{item}", use_container_width=True):
            if item == "My borrowings":
                st.switch_page("pages/04_Borrowings.py")
            elif item == "My posts":
                st.switch_page("pages/05_Posts_Reviews.py")
            elif item == "History":
                st.switch_page("pages/06_Reading_History.py")
            elif item == "Settings":
                st.switch_page("pages/09_Settings.py")


with profile_col:
    avatar_col, info_col, edit_col = st.columns([0.8, 3, 1.2])

    with avatar_col:
        st.markdown(
            render_avatar(reader_initials(current_reader["Name"]), COLORS["gold"], COLORS["brown"], "large"),
            unsafe_allow_html=True,
        )

    with info_col:
        st.markdown(
            f'<h2 style="margin-bottom:2px;">{escape(current_reader["Name"])}</h2>'
            f'<span class="muted">Reader since {escape(str(current_reader.get("Created_At") or "unknown"))}</span><br>',
            unsafe_allow_html=True,
        )
        earned_badges = [badge for badge in reader_badges if badge["earned"]]
        if earned_badges:
            badges_html = " ".join(render_badge(badge["name"], "green") for badge in earned_badges)
            st.markdown(badges_html, unsafe_allow_html=True)

    with edit_col:
        page_spacer(10)
        if st.button("Edit profile", key="edit_prof_btn"):
            st.switch_page("pages/09_Settings.py")

    page_spacer(16)
    st.markdown("<hr>", unsafe_allow_html=True)

    stats = [
        (str(current_reader.get("Points") or 0), "Reader points"),
        (str(reader_stats["posts_published"]), "Posts published"),
        (str(reader_stats["avg_rating"]), "Avg. rating"),
        (str(len(get_reader_genres(current_reader))), "Preferred genres"),
    ]

    stat_cols = st.columns(4)
    for index, (value, label) in enumerate(stats):
        with stat_cols[index]:
            st.markdown(
                f'<div style="text-align:center;">'
                f'<div style="font-family: Playfair Display, Georgia, serif; '
                f'font-size:1.6rem; font-weight:700; color:{COLORS["dark_green"]};">{escape(value)}</div>'
                f'<div class="muted" style="font-size:0.78rem;">{escape(label)}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    page_spacer(20)
    st.markdown("<hr>", unsafe_allow_html=True)

    section_title("Reader preferences")

    show_history = st.toggle(
        "Show my reading history",
        value=bool(current_reader.get("Show_Reading_History")),
        key="priv_history",
    )
    receive_recs = st.toggle(
        "Receive recommendations",
        value=bool(current_reader.get("Receive_Recommendations")),
        key="priv_recs",
    )

    if st.button("Save reader preferences", type="primary", key="save_priv"):
        success, message = update_reader_profile(
            reader_id=current_reader["Reader_ID"],
            name=current_reader["Name"],
            preferred_category=current_reader.get("Preferred_Category") or "",
            receive_recommendations=receive_recs,
            show_reading_history=show_history,
        )
        if success:
            st.success("Reader preferences saved.")
        else:
            st.error(message)

    page_spacer(20)
    st.markdown("<hr>", unsafe_allow_html=True)

    section_title("Preferred genres")
    genres = get_reader_genres(current_reader)
    if genres:
        st.markdown(" ".join(render_badge(genre, "green") for genre in genres), unsafe_allow_html=True)
    else:
        st.markdown('<p class="muted">No preferred genres saved yet.</p>', unsafe_allow_html=True)

    page_spacer(20)
    st.markdown("<hr>", unsafe_allow_html=True)

    section_title("Badge progress")
    for badge in reader_badges:
        st.markdown(
            f'<span class="muted" style="font-size:0.82rem;">'
            f'{escape(badge["name"])} - {escape(badge["description"])}</span>',
            unsafe_allow_html=True,
        )
        st.markdown(render_progress_bar(badge["progress"]), unsafe_allow_html=True)


with posts_col:
    section_title("Latest posts")

    if not reader_posts:
        st.markdown('<p class="muted">No reader posts yet.</p>', unsafe_allow_html=True)

    for post in reader_posts:
        st.markdown(
            f'<div class="card">'
            f'<strong class="secondary">{escape(post.get("book_title") or "Unlinked book")}</strong><br>'
            f'<span class="muted" style="font-size:0.82rem;">'
            f'{escape((post.get("content") or "")[:90])}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
