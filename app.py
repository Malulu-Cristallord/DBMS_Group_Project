from html import escape
import os
import sys

import streamlit as st
from Backend.Functions.saved_books import save_book

sys.path.insert(0, os.path.dirname(__file__))

from Backend.Functions.post_handler import(
    add_like,
    get_like_count,
    remove_like,
    has_liked,
    create_comment,
    get_comments,
)


from Backend.Functions.library_data import (
    get_book_by_isbn,
    get_popular_books,
    get_posts,
    get_personalized_recommendations,
    get_reader_from_session,
    increment_book_clicked,
    reader_initials,
    update_recommendation_status,
)
from components.ui_helpers import (
    COLORS,
    inject_global_css,
    page_spacer,
    render_avatar,
    render_badge,
    render_book_cover,
    render_login_required,
    render_navbar,
    render_stars,
    section_title, render_navigation_section,
)
from UI.Login.session import google_user_is_logged_in, sync_google_user_to_session


st.set_page_config(
    page_title="LibTrack | Home",
    page_icon="LT",
    layout="wide",
)

inject_global_css()


if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if google_user_is_logged_in(st.user) and not st.session_state["logged_in"]:
    google_success, google_message, _ = sync_google_user_to_session(
        st.session_state,
        st.user,
    )

    if not google_success:
        render_navbar(active_page="Discover")
        st.error(google_message)
        if st.button("Sign out of Google", type="primary"):
            st.logout()
        st.stop()

if not st.session_state["logged_in"]:
    render_navbar(active_page="Discover")
    render_login_required("Please sign in to access your LibTrack home page.")
    st.stop()


current_reader = get_reader_from_session(st.session_state)

if current_reader is None:
    render_navbar(active_page="Discover")
    render_login_required(
        "Could not load your reader profile. Please log in again.",
        title="Profile unavailable",
        clear_session=True,
    )
    st.stop()


render_navbar(active_page="Discover")
page_spacer(24)

col_welcome, col_action = st.columns([3, 1])

with col_welcome:
    reader_first_name = (current_reader["Name"] or "reader").split()[0]
    st.markdown(
        f'<h1 style="margin-bottom:4px;">Welcome back, {escape(reader_first_name)}</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="secondary">Discover your next great read and share your journey.</p>',
        unsafe_allow_html=True,
    )

with col_action:
    page_spacer(10)
    if st.button("Create a post", type="primary", use_container_width=True):
        st.switch_page("pages/07_Create_Post.py")
    if st.button("My posts", use_container_width=True):
        st.switch_page("pages/13_My_Posts.py")


page_spacer(10)

#--------------------------------------------------------------------SEARCH BAR

search_query = st.text_input(
    "",
    placeholder="Search for a book, author, or genre...",
    label_visibility="collapsed",
    key="home_search",
)

if search_query:
    st.session_state["book_search_query"] = search_query
    st.info(f"Searching for: **{search_query}**. Open Book Discovery for full results.")

    if st.button("Open Book Discovery"):
        st.switch_page("pages/03_Discovery.py")


page_spacer(20)

#--------------------------------------------------------------------RECOMMENDATION

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

section_title("Recommend to You")

recommended_books = get_personalized_recommendations(current_reader["Reader_ID"], limit=4)

if not recommended_books:
    st.info("No recommended books found yet. Add books to the database or update your preferred categories.")
else:
    rec_cols = st.columns(min(len(recommended_books), 4))

    for index, book in enumerate(recommended_books[:4]):
        with rec_cols[index]:
            st.markdown(render_book_cover(book["cover"], size="card"), unsafe_allow_html=True)
            st.markdown(
                f'<strong style="font-size:0.9rem; color:{COLORS["dark_green"]};">'
                f'{escape(book["title"])}</strong>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<span class="muted">{escape(book["author"])}</span><br>'
                f'{render_stars(book["avg_rating"])}',
                unsafe_allow_html=True,
            )

            if st.button("View", key=f"rec_{book['id']}", use_container_width=True):
                increment_book_clicked(book["id"])
                update_recommendation_status(current_reader["Reader_ID"], book["id"], "clicked")
                st.session_state["selected_book_id"] = book["id"]
                st.switch_page("pages/15_Book_Detail.py")

            if st.button("Save", key=f'save_{book["isbn"]}', use_container_width=True):
                result = save_book(book["isbn"], current_reader["Reader_ID"])
                if result["success"]:
                    update_recommendation_status(current_reader["Reader_ID"], book["isbn"], "saved")
                    st.success("Saved.")
                else:
                    st.info(result["message"])
page_spacer(20)

#--------------------------------------------------------------------ADD NEW BOOKS

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

section_title("Got a new book to add into the database?")
if st.button("Add a new book to our database", type="primary", use_container_width=True):
    st.switch_page("pages/11_Add_Books.py")

page_spacer(20)

#--------------------------------------------------------------------POPULAR BOOKS

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

section_title("Popular Books")

popular_books = get_popular_books(limit=6)

if not popular_books:
    st.info("No books found yet. Please insert book data into the books table.")
else:
    pop_cols = st.columns(min(len(popular_books), 6))

    for index, book in enumerate(popular_books[:6]):
        with pop_cols[index]:
            st.markdown(render_book_cover(book["cover"], size="card"), unsafe_allow_html=True)
            st.markdown(
                f'<span style="font-size:0.8rem; font-weight:600; min-height=100px; color:{COLORS["dark_green"]};">'
                f'{escape(book["title"])}</span><br>'
                f'<span class="muted" style="font-size:0.75rem;">{escape(book["author"])}</span>',
                unsafe_allow_html=True,
            )
            if st.button("View", key=f"pop_{book['id']}", use_container_width=True):
                increment_book_clicked(book["id"])
                update_recommendation_status(current_reader["Reader_ID"], book["id"], "clicked")
                st.session_state["selected_book_id"] = book["id"]
                st.switch_page("pages/15_Book_Detail.py")

            if st.button("Save", key=f'save_pop_{book["isbn"]}', use_container_width=True):
                result = save_book(book["isbn"], current_reader["Reader_ID"])
                if result["success"]:
                    update_recommendation_status(current_reader["Reader_ID"], book["isbn"], "saved")
                    st.success("Saved.")
                else:
                    st.info(result["message"])


page_spacer(20)

#--------------------------------------------------------------------ACTIVITY FEED

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

section_title("Activity feed")

activity_posts = get_posts(limit=10)

if not activity_posts:
    st.info("No activity yet. Posts will appear here after readers create posts.")
else:
    for post in activity_posts:
        reader_name = post.get("reader_name") or "Unknown reader"
        book_title = post.get("book_title") or "an unlinked book"
        content = post.get("content") or "No content."

        col_post, col_tag = st.columns([5, 1])

        with col_post:
            likes = int(post.get("upvote_count") or 0)
            st.markdown(
                f"""
                <div class="card">
                    <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
                        {render_avatar(reader_initials(reader_name), COLORS["sage"] if "sage" in COLORS else COLORS["light_green"], COLORS["dark_green"])}
                        <div>
                            <strong style="font-size:0.95rem;">{escape(reader_name)}</strong>
                            <span class="muted">
                                post <strong>{escape(book_title)}</strong> on {escape(str(post.get("created_at") or ""))}
                            </span>
                        </div>
                    </div>
                    <p style="margin:6px 0 10px 0; font-size:0.92rem; line-height:1.55;">
                        {escape(content)}
                    </p>
                    <div class="action-row">
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            liked = has_liked(
                post["post_id"],
                current_reader["Reader_ID"]
            )

            heart = "❤️" if liked else "🤍"
            likes = get_like_count(post["post_id"])

            if st.button(
                f"{heart} {likes}",
                key=f"like_{post['post_id']}"
                
            ):

                if liked:
                    remove_like(
                        post["post_id"],
                        current_reader["Reader_ID"]
                    )
                else:
                    add_like(
                        post["post_id"],
                        current_reader["Reader_ID"]
                    )

                st.rerun()

            comments = get_comments(post["post_id"])
            st.caption(f"💬 {len(comments)} comments")

            with st.expander("Comments"):

                if not comments:
                    st.caption("No comments yet.")

                for comment in comments:

                    st.markdown(
                        f"""
                        <div style="
                            padding:10px;
                            border-radius:12px;
                            background:#f7f7f7;
                            margin-bottom:8px;
                        ">
                            <strong>
                                {escape(comment["reader_name"])}
                            </strong>
                                {escape(comment["content"])}

                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                new_comment = st.text_input(
                    "Add a comment...",
                    key=f"comment_input_{post['post_id']}"
                )

                if st.button(
                    "Post",
                    key=f"comment_btn_{post['post_id']}"
                ):

                    if new_comment.strip():

                        create_comment(
                            post["post_id"],
                            current_reader["Reader_ID"],
                            new_comment,
                        )

                        st.rerun()

        with col_tag:
            page_spacer(8)

            if st.button("Book Details", key=f"feed_detail_{post['post_id']}"):
                selected_book = get_book_by_isbn(post.get("isbn"))
                if selected_book:
                    increment_book_clicked(selected_book["id"])
                    st.session_state["selected_book_id"] = selected_book["id"]
                    st.switch_page("pages/15_Book_Detail.py")
                else:
                    st.toast("This post is not linked to a book.")


page_spacer(20)
#--------------------------------------------------------------------NAVIGATION
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
section_title("Navigation")
render_navigation_section()



