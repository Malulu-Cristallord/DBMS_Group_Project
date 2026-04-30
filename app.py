# =============================================================================
# FILE: app.py
# PURPOSE: Main entry point for the LibTrack Streamlit application.
#          This file configures the app-wide settings and serves as the
#          landing/home feed page.
#
# HOW TO RUN:
#   streamlit run app.py
#
# BACK-END INTEGRATION:
#   - Reader data comes from the readers table.
#   - Book data comes from the books table.
#   - Activity feed data comes from posts joined with readers and books.
# =============================================================================

import streamlit as st
import sys
import os

# Add the project root to the Python path so we can import our modules.
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

from Backend.DB_Stuff.db_connect import get_connection


# =============================================================================
# DATABASE HELPER FUNCTIONS
# =============================================================================

def fetch_one(query, params=None):
    connection = get_connection()
    if connection is None:
        return None

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(query, params or ())
        return cursor.fetchone()

    except Exception as e:
        st.error(f"Database query failed: {e}")
        return None

    finally:
        cursor.close()
        connection.close()


def fetch_all(query, params=None):
    connection = get_connection()
    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(query, params or ())
        return cursor.fetchall()

    except Exception as e:
        st.error(f"Database query failed: {e}")
        return []

    finally:
        cursor.close()
        connection.close()


def get_current_reader():
    """
    Get the currently logged-in reader from the database.

    The login page should store:
        st.session_state["reader_id"]
    """

    reader_id = st.session_state.get("reader_id")

    if not reader_id:
        return None

    return fetch_one(
        """
        SELECT
            Reader_ID AS reader_id,
            Name AS name,
            Email AS email,
            Preferred_Category AS preferred_category,
            Points AS points,
            Receive_Recommendations AS receive_recommendations,
            Show_Reading_History AS show_reading_history
        FROM readers
        WHERE Reader_ID = %s
        """,
        (reader_id,)
    )


def get_recommended_books(reader):
    """
    Get recommended books based on the reader's preferred category.

    Current simple rule:
    - If the reader has preferred categories, show books whose Category matches.
    - Otherwise, show books ordered by Rating.
    """

    if reader and reader.get("preferred_category"):
        preferred_categories = [
            category.strip()
            for category in reader["preferred_category"].split(",")
            if category.strip()
        ]

        if preferred_categories:
            placeholders = ", ".join(["%s"] * len(preferred_categories))

            return fetch_all(
                f"""
                SELECT
                    Book_ID AS id,
                    Title AS title,
                    Author AS author,
                    Category AS category,
                    Cover AS cover,
                    Rating AS avg_rating
                FROM books
                WHERE Category IN ({placeholders})
                ORDER BY Rating DESC
                LIMIT 4
                """,
                tuple(preferred_categories)
            )

    return fetch_all(
        """
        SELECT
            Book_ID AS id,
            Title AS title,
            Author AS author,
            Category AS category,
            Cover AS cover,
            Rating AS avg_rating
        FROM books
        ORDER BY Rating DESC
        LIMIT 4
        """
    )


def get_popular_books():
    """
    Get popular books.

    Since the current books table does not have click_count or save_count yet,
    this version uses Rating as the popularity signal.
    """

    return fetch_all(
        """
        SELECT
            Book_ID AS id,
            Title AS title,
            Author AS author,
            Category AS category,
            Cover AS cover,
            Rating AS avg_rating
        FROM books
        ORDER BY Rating DESC
        LIMIT 6
        """
    )


def get_activity_feed():
    """
    Get recent activity feed from posts joined with readers and books.
    """

    return fetch_all(
        """
        SELECT
            p.Post_ID AS post_id,
            p.Reader_ID AS reader_id,
            p.Book_ID AS book_id,
            p.Review AS review,
            p.Rating AS rating,
            p.Upvote_Count AS upvote_count,
            p.Created_At AS created_at,
            r.Name AS reader_name,
            b.Title AS book_title
        FROM posts p
        JOIN readers r ON p.Reader_ID = r.Reader_ID
        JOIN books b ON p.Book_ID = b.Book_ID
        ORDER BY p.Created_At DESC
        LIMIT 10
        """
    )


def get_initials(name):
    if not name:
        return "?"

    words = name.split()

    if len(words) == 1:
        return words[0][0].upper()

    return "".join(word[0].upper() for word in words[:2])


def get_cover_value(book):
    """
    render_book_cover() in the current UI expects a visual value.
    If the database has no cover value, use a safe fallback color.
    """

    return book.get("cover") or COLORS["sage"]


# =============================================================================
# PAGE CONFIGURATION
# Must be the FIRST Streamlit command in every file.
# =============================================================================

st.set_page_config(
    page_title="LibTrack — Your Reading Journey",
    page_icon="📖",
    layout="wide"
)

inject_global_css()


# =============================================================================
# AUTH CHECK
# =============================================================================

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    render_navbar(active_page="discover")
    page_spacer(40)

    st.warning("Please sign in to access your LibTrack home page.")

    if st.button("Go to Login", type="primary"):
        st.switch_page("pages/01_Login.py")

    st.stop()


# =============================================================================
# LOAD CURRENT READER
# =============================================================================

current_reader = get_current_reader()

if current_reader is None:
    render_navbar(active_page="discover")
    page_spacer(40)

    st.error("Could not load your reader profile. Please log in again.")

    if st.button("Go to Login", type="primary"):
        st.session_state.clear()
        st.switch_page("pages/01_Login.py")

    st.stop()


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
    reader_first_name = current_reader["name"].split()[0]

    st.markdown(
        f'<h1 style="margin-bottom:4px;">Welcome back, {reader_first_name} 👋</h1>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<p class="secondary">Discover your next great read and share your journey.</p>',
        unsafe_allow_html=True,
    )

with col_action:
    page_spacer(10)

    if st.button("✏️ Create a post", type="primary", use_container_width=True):
        st.switch_page("pages/07_Create_Post.py")


page_spacer(10)


# =============================================================================
# QUICK SEARCH BAR
# =============================================================================

search_query = st.text_input(
    "",
    placeholder="🔍  Search for a book, author, or genre...",
    label_visibility="collapsed",
    key="home_search",
)

if search_query:
    st.session_state["book_search_query"] = search_query
    st.info(f"Searching for: **{search_query}** — go to the Book Discovery page for full results.")

    if st.button("Open Book Discovery"):
        st.switch_page("pages/03_Discovery.py")


page_spacer(20)
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)


# =============================================================================
# RECOMMENDED BOOKS SECTION
# =============================================================================

section_title("📚 Recommended for you")

recommended_books = get_recommended_books(current_reader)

if not recommended_books:
    st.info("No recommended books found yet. Add more books to the database or update your preferred categories.")

else:
    rec_cols = st.columns(4)

    for i, book in enumerate(recommended_books[:4]):
        with rec_cols[i]:
            st.markdown(
                render_book_cover(get_cover_value(book), size="card"),
                unsafe_allow_html=True
            )

            st.markdown(
                f'<strong style="font-size:0.9rem; color:{COLORS["dark_green"]};">'
                f'{book["title"]}</strong>',
                unsafe_allow_html=True,
            )

            st.markdown(
                f'<span class="muted">{book.get("author") or "Unknown author"}</span><br>'
                f'{render_stars(float(book.get("avg_rating") or 0))}',
                unsafe_allow_html=True,
            )

            if st.button("View", key=f"rec_{book['id']}", use_container_width=True):
                st.session_state["selected_book_id"] = book["id"]
                st.switch_page("pages/05_Book_Detail.py")


page_spacer(20)
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)


if st.button("Find books", type="primary"):
    st.switch_page("pages/03_Discovery.py")


# =============================================================================
# POPULAR BOOKS OF THE WEEK
# =============================================================================

section_title("🔥 Popular this week")

popular_books = get_popular_books()

if not popular_books:
    st.info("No books found yet. Please insert book data into the books table.")

else:
    pop_cols = st.columns(6)

    for i, book in enumerate(popular_books[:6]):
        with pop_cols[i]:
            st.markdown(
                render_book_cover(get_cover_value(book), size="card"),
                unsafe_allow_html=True
            )

            st.markdown(
                f'<span style="font-size:0.8rem; font-weight:600; color:{COLORS["dark_green"]};">'
                f'{book["title"]}</span><br>'
                f'<span class="muted" style="font-size:0.75rem;">'
                f'{book.get("author") or "Unknown author"}</span>',
                unsafe_allow_html=True,
            )


page_spacer(20)
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)


# =============================================================================
# COMMUNITY FEED
# =============================================================================

section_title("🌿 Activity feed")

activity_posts = get_activity_feed()

if not activity_posts:
    st.info("No activity yet. Reviews will appear here after readers create posts.")

else:
    for post in activity_posts:
        rating_html = ""

        if post.get("rating"):
            rating_html = render_stars(int(post["rating"]))

        format_html = render_badge("Review", style="beige")

        reader_name = post.get("reader_name") or "Unknown reader"
        reader_initials = get_initials(reader_name)

        review_content = post.get("review") or "No review content."

        col_post, col_tag = st.columns([5, 1])

        with col_post:
            st.markdown(
                f"""
                <div class="card">
                    <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
                        {render_avatar(reader_initials, COLORS["sage"], COLORS["dark_green"])}
                        <div>
                            <strong style="font-size:0.95rem;">{reader_name}</strong>
                            <span class="muted">
                                reviewed <strong>{post["book_title"]}</strong> · {post["created_at"]}
                            </span>
                        </div>
                        <div style="margin-left:auto;">{rating_html}</div>
                    </div>
                    <p style="margin:6px 0 10px 0; font-size:0.92rem; line-height:1.55;">
                        {review_content}
                    </p>
                    <div class="action-row">
                        ♡ {post.get("upvote_count") or 0} likes &nbsp;&nbsp; 💬 comments coming soon
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_tag:
            page_spacer(8)
            st.markdown(format_html, unsafe_allow_html=True)

            if st.button("♡ Like", key=f"like_{post['post_id']}"):
                st.toast("Like feature will be connected to the database later.")

            if st.button("💬 Comment", key=f"comment_{post['post_id']}"):
                st.toast("Comments coming soon!")


page_spacer(20)