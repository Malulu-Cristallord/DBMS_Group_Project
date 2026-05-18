from html import escape
import os
import sys

import streamlit as st
from streamlit import session_state

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Backend.Functions.library_data import  get_reviews, reader_initials, get_book_by_isbn
from components.ui_helpers import (
    COLORS,
    inject_global_css,
    page_spacer,
    render_avatar,
    render_badge,
    render_book_cover,
    render_navbar,
    render_stars,
    section_title,
)

st.set_page_config(
    page_title="Book Detail | LibTrack",
    page_icon="LT",
    layout="wide",
)

inject_global_css()
render_navbar(active_page="discover")
page_spacer(20)

#current_isbn = "9780439362139"
#book = get_book_by_isbn(current_isbn)

book = get_book_by_isbn(st.session_state.get("selected_book_id"))


if not book:
    st.warning("No books are available in the database yet.")
    if st.button("Back to Discovery"):
        st.switch_page("pages/03_Discovery.py")
    st.stop()

#book_reviews = get_reviews(isbn=book["id"], limit=20)

page_spacer(10)

if "search_keyword" not in session_state:
    session_state["search_keyword"] = ""

# Quick Search section
search_col, button_col = st.columns([6, 1])

with search_col:
    search_input = st.text_input(
        "Search books",
        value=st.session_state["search_keyword"],
        placeholder="Search by title, author, or ISBN...",
        label_visibility="collapsed",
    )

with button_col:
    search_clicked = st.button(
        "Confirm",
        type="primary",
        use_container_width=True,
    )

# Handle search
if search_clicked:
    st.session_state["search_keyword"] = search_input

    # Example: search by ISBN
    searched_book = get_book_by_isbn(search_input)

    if searched_book:
        book = searched_book
    else:
        st.warning("No matching book found.")
        st.stop()




# Main
main_col, meta_col = st.columns([3, 1])

with main_col:
    header_cols = st.columns([1, 4])

    # The cover uses API from open library, which fetches images directly from their db
    # However, a default cover is needed in future updates

    with header_cols[0]:
        if book.get("cover") is not None:
            st.image(book["cover"])
        else:
            st.image("Resources/Book Covers/Cover_Default.png")

        
    with header_cols[1]:
        genres = book.get("genre") or []
        genre_text = "".join(genres) if genres else "Uncategorized"

        st.markdown(
            f'<h1 style="font-size:2rem; margin-bottom:4px;">{escape(book["title"])}</h1>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<p class="secondary" style="font-size:1rem; margin-bottom:10px;">'
            f'{escape(book["author"])} - {escape(genre_text)} - {escape(str(book["year"]))}</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'{render_stars(book["avg_rating"])} '
            f'<span class="muted">- {book["review_count"]} reviews</span>',
            unsafe_allow_html=True,
        )

        page_spacer(10)
        st.markdown(
            f'{render_badge("In books table", "available")} '
            f'{render_badge(genre_text, "beige")}',
            unsafe_allow_html=True,
        )

        page_spacer(14)
        btn_cols = st.columns(2)
        with btn_cols[0]:
            if st.button("Write / Edit review", type="primary", key="write_review_top"):
                st.session_state["review_book_isbn"] = book["isbn"]
                st.switch_page("pages/06_Create_Review.py")

        with btn_cols[1]:
            if st.button("Create post", key="create_post_top"):
                st.session_state["post_book_isbn"] = book["isbn"]
                st.switch_page("pages/07_Create_Post.py")


with meta_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(
        '<p style="font-size:0.8rem; font-weight:600; text-transform:uppercase; margin-bottom:12px;">Book data</p>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<p class="secondary" style="margin-bottom:4px;">ISBN</p>'
        f'<strong>{escape(book["isbn"] or "Not set")}</strong>',
        unsafe_allow_html=True,
    )

    page_spacer(10)

    st.markdown(
        f'<p class="secondary" style="margin-bottom:4px;">Publisher</p>'
        f'<strong>{escape(book["publisher"] or "Not set")}</strong>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


page_spacer(20)
st.markdown("<hr>", unsafe_allow_html=True)

section_title("Description")
st.markdown(
    f'<p style="font-size:0.97rem; line-height:1.7; max-width:720px; color:{COLORS["text_secondary"]};">'
    f'{escape(book["description"])}</p>',
    unsafe_allow_html=True,
)

page_spacer(20)
st.markdown("<hr>", unsafe_allow_html=True)

section_title("Community reviews")

if st.button("Back to Discovery"):
    st.switch_page("pages/03_Discovery.py")

if book_reviews := get_reviews(isbn=book["isbn"], limit=20):
    for review in book_reviews:
        reader_name = review.get("reader_name") or "Unknown reader"
        rating_html = render_stars(review["rating"]) if review.get("rating") else ""
        st.markdown(
            f"""
            <div class="card">
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
                    {render_avatar(reader_initials(reader_name), COLORS["light_green"], COLORS["dark_green"])}
                    <div style="flex:1;">
                        <strong>{escape(reader_name)}</strong>
                        {rating_html}
                    </div>
                    <span class="muted">{escape(str(review.get("created_at") or ""))}</span>
                </div>
                <p style="font-size:0.93rem; line-height:1.6; margin:0;">{escape(review.get("content") or "")}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.markdown(
        '<p class="muted">No reviews yet. Be the first reader to share your thoughts.</p>',
        unsafe_allow_html=True,
    )
