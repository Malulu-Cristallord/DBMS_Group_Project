# =============================================================================
# FILE: pages/17_Saved_Books.py
# PURPOSE: "Book Show" — Visual showcase of books saved by the user from
#          the Recommendations page.
#
# FRONT-END ONLY. No backend, no persistent data.
#
# FUTURE BACK-END INTEGRATION:
#   - Saved books list:  GET /api/wishlist?user_id=<id>&source=recommendations
#   - Remove from saved: DELETE /api/wishlist/<item_id>
#   - Borrow action:     POST /api/borrowings { book_id, format }
#   - Book details nav:  GET /api/books/<book_id>
# =============================================================================

import streamlit as st
import sys, os

from Backend.Functions.library_data import get_reader_from_session
from Backend.Functions.saved_books import get_saved_books

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.ui_helpers import (
    inject_global_css, render_navbar,
    cover, badge, stars, progress_bar,
    section_title, section_label, spacer, COLORS, COVER_COLORS, render_login_required,
)

current_reader = get_reader_from_session(st.session_state)
if current_reader is None:
    render_login_required("Please sign in to view reading history.")
    st.stop()


# ── Page config ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Book Show — LibTrack",
    page_icon="📖",
    layout="wide",
)
inject_global_css()
render_navbar("Saved_Books")

# ── Additional CSS specific to this page ──────────────────────────────────
st.markdown("""
<style>
/* Hero horizontal book strip */
.show-hero {
    background: #1F3F2E;
    border-radius: 16px;
    padding: 40px 36px 32px;
    margin-bottom: 40px;
    position: relative;
    overflow: hidden;
}
.show-hero::before {
    content: '';
    position: absolute; right: -80px; top: -80px;
    width: 320px; height: 320px; border-radius: 50%;
    background: rgba(210,179,84,0.1);
    pointer-events: none;
}
.show-hero-top {
    display: flex; justify-content: space-between;
    align-items: flex-start; margin-bottom: 28px;
}
.show-hero-text h2 {
    font-family: 'Playfair Display', serif !important;
    color: white !important; font-size: 1.7rem !important;
    margin-bottom: 6px !important;
}
.show-hero-text p { color: rgba(255,255,255,0.65); font-size: 0.88rem; line-height: 1.6; }
.show-hero-stat {
    text-align: right; flex-shrink: 0;
}
.show-hero-stat .num {
    font-family: 'Playfair Display', serif;
    font-size: 2.8rem; font-weight: 700; color: #D2B354; line-height: 1;
}
.show-hero-stat .lbl {
    font-size: 0.75rem; color: rgba(255,255,255,0.5);
    text-transform: uppercase; letter-spacing: .1em;
}

/* Horizontal scrollable book strip inside hero */
.hero-shelf {
    display: flex; gap: 18px; overflow-x: auto; padding-bottom: 8px;
}
.hero-shelf::-webkit-scrollbar { height: 3px; }
.hero-shelf::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.3); border-radius: 2px; }
.hero-book-item {
    flex-shrink: 0; display: flex; align-items: center;
    gap: 14px; cursor: pointer;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 10px; padding: 12px 16px 12px 12px;
    transition: background .2s, transform .2s;
    min-width: 220px;
}
.hero-book-item:hover {
    background: rgba(255,255,255,0.12);
    transform: translateY(-2px);
}
.hero-cover-sm {
    width: 52px; height: 74px; border-radius: 5px; flex-shrink: 0;
    position: relative;
}
.hero-cover-sm::after {
    content: ''; position: absolute; left: 0; top: 0; bottom: 0;
    width: 6px; background: rgba(0,0,0,0.2); border-radius: 5px 0 0 5px;
}
.hero-book-title {
    font-family: 'Playfair Display', serif;
    color: white; font-size: 0.9rem; font-weight: 600;
    line-height: 1.3; margin-bottom: 3px;
}
.hero-book-author { color: rgba(255,255,255,0.55); font-size: 0.75rem; }
.hero-book-rating { color: #D2B354; font-size: 0.78rem; margin-top: 6px; }

/* Grid book cards */
.book-grid-card {
    background: white; border-radius: 14px;
    border: 1px solid #EBEBEB;
    padding: 0; overflow: hidden;
    transition: all .25s; cursor: pointer;
}
.book-grid-card:hover {
    border-color: #3E7255;
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(31,63,46,0.1);
}
.book-grid-cover {
    width: 100%; height: 180px; border-radius: 0;
    display: block; position: relative;
}
.book-grid-cover::after {
    content: ''; position: absolute; left: 0; top: 0; bottom: 0;
    width: 9px; background: rgba(0,0,0,0.2);
}
.book-grid-body { padding: 14px 16px 16px; }
.book-grid-title {
    font-family: 'Playfair Display', serif;
    font-size: 0.95rem; font-weight: 600; color: #1F3F2E;
    margin-bottom: 2px; line-height: 1.3;
}
.book-grid-author { font-size: 0.78rem; color: #8A8A8A; margin-bottom: 8px; }
.book-grid-meta { display: flex; align-items: center; justify-content: space-between; }

/* Category filter pills */
.filter-row { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 24px; }
.filter-pill {
    padding: 6px 16px; border-radius: 20px; font-size: 0.82rem; cursor: pointer;
    border: 1.5px solid #1F3F2E; color: #1F3F2E; background: white;
    font-family: 'Source Serif 4', serif; transition: all .2s;
}
.filter-pill.active { background: #1F3F2E; color: white; }

/* Reading list section */
.reading-item {
    display: flex; align-items: center; gap: 16px;
    padding: 14px 0; border-bottom: 1px solid #F0F0F0;
}
.reading-item:last-child { border-bottom: none; }
.reading-item-info { flex: 1; }
.reading-item-title { font-size: 0.95rem; font-weight: 600; color: #1F3F2E; margin-bottom: 2px; }
.reading-item-author { font-size: 0.8rem; color: #8A8A8A; }
.reading-item-badge { margin-top: 6px; }

/* Remove button */
.remove-btn {
    color: #AAAAAA; font-size: 0.8rem; cursor: pointer; padding: 4px 8px;
    border-radius: 4px; transition: color .2s;
}
.remove-btn:hover { color: #654421; }

/* Insight card */
.insight-card {
    background: #DFF2DF; border-radius: 12px;
    padding: 18px 20px; border: 1px solid rgba(31,63,46,0.15);
    margin-bottom: 12px;
}
.insight-icon { font-size: 1.4rem; margin-bottom: 6px; }
.insight-text { font-size: 0.85rem; color: #3A3A3A; line-height: 1.5; }
</style>
""", unsafe_allow_html=True)

spacer(24)

# =============================================================================
# PLACEHOLDER DATA — Replace with API calls in production
# In production: GET /api/wishlist?user_id=<id>&source=recommendations
# =============================================================================
SAVED_BOOKS = get_saved_books(reader_id)

# =============================================================================
# HERO BANNER — Saved Books Showcase
# =============================================================================
hero_books_html = ""
for b in SAVED_BOOKS[:5]:
    rating_stars = "★" * int(b["rating"]) + "☆" * (5 - int(b["rating"]))
    hero_books_html += f"""
    <div class="hero-book-item">
        <div class="hero-cover-sm" style="background:{b['color']};"></div>
        <div>
            <div class="hero-book-title">{b['title']}</div>
            <div class="hero-book-author">{b['author']}</div>
            <div class="hero-book-rating">{rating_stars} {b['rating']}</div>
        </div>
    </div>
    """

st.markdown(f"""
<div class="show-hero">
    <div class="show-hero-top">
        <div class="show-hero-text">
            <span style="background:#D2B354;color:#654421;padding:4px 14px;
                border-radius:20px;font-size:0.75rem;font-weight:600;
                display:inline-block;margin-bottom:12px;">📚 My Saved Books</span>
            <h2>Your reading wishlist</h2>
            <p>Books you saved from Recommendations.<br>
               Ready to borrow whenever you are.</p>
        </div>
        <div class="show-hero-stat">
            <div class="num">{len(SAVED_BOOKS)}</div>
            <div class="lbl">books saved</div>
        </div>
    </div>
    <div class="hero-shelf">
        {hero_books_html}
    </div>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# CATEGORY FILTER
# In production: sends category param to GET /api/wishlist?category=...
# =============================================================================
all_categories = ["All"] + sorted(set(b["category"] for b in SAVED_BOOKS))

if "show_category" not in st.session_state:
    st.session_state["show_category"] = "All"

filter_html = '<div class="filter-row">'
for cat in all_categories:
    active_cls = "filter-pill active" if st.session_state["show_category"] == cat else "filter-pill"
    filter_html += f'<span class="{active_cls}" onclick="">{cat}</span>'
filter_html += '</div>'
st.markdown(filter_html, unsafe_allow_html=True)

# Streamlit radio as actual filter (functional)
selected_cat = st.radio(
    "Filter by category",
    options=all_categories,
    horizontal=True,
    label_visibility="collapsed",
    key="cat_filter",
)
st.session_state["show_category"] = selected_cat

# Apply filter
filtered = (
    SAVED_BOOKS if selected_cat == "All"
    else [b for b in SAVED_BOOKS if b["category"] == selected_cat]
)

spacer(8)

# =============================================================================
# TWO-COLUMN LAYOUT: Book grid (left) + Sidebar insights (right)
# =============================================================================
grid_col, sidebar_col = st.columns([3, 1.2])

# ── LEFT: Book grid ───────────────────────────────────────────────────────
with grid_col:
    section_title(f"Saved books · {len(filtered)} title{'s' if len(filtered)!=1 else ''}")

    # Display books in rows of 3
    for row_start in range(0, len(filtered), 3):
        row_books = filtered[row_start: row_start + 3]
        cols = st.columns(3)
        for i, book in enumerate(row_books):
            with cols[i]:
                avail_style = "green" if book["status"] == "Available" else "grey"

                st.markdown(f"""
                <div class="book-grid-card">
                    <div class="book-grid-cover"
                         style="background:{book['color']};"></div>
                    <div class="book-grid-body">
                        <div class="book-grid-title">{book['title']}</div>
                        <div class="book-grid-author">{book['author']}</div>
                        <div class="book-grid-meta">
                            <span style="color:#D2B354;font-size:.8rem;">
                                {"★"*int(book['rating'])} {book['rating']}
                            </span>
                            <span class="lt-badge lt-badge-{avail_style}"
                                  style="font-size:.72rem;">
                                {book['status']}
                            </span>
                        </div>
                        <div style="margin-top:8px;">
                            <span class="lt-badge lt-badge-beige"
                                  style="font-size:.7rem;">{book['category']}</span>
                            <span style="font-size:.7rem;color:#D2B354;margin-left:6px;">
                                ✦ {book['match']}
                            </span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                spacer(6)

                # In production: POST /api/borrowings { book_id }
                if st.button(
                    "Borrow" if book["status"] == "Available" else "Reserve",
                    key=f"borrow_{book['id']}",
                    use_container_width=True,
                    type="primary" if book["status"] == "Available" else "secondary",
                ):
                    st.toast(f"'{book['title']}' — action confirmed!")

                # In production: DELETE /api/wishlist/<item_id>
                if st.button("Remove", key=f"remove_{book['id']}", use_container_width=True):
                    st.toast(f"'{book['title']}' removed from your list.")

        spacer(12)

# ── RIGHT: Insights sidebar ───────────────────────────────────────────────
with sidebar_col:
    spacer(4)
    section_title("Insights")

    # Category distribution
    category_counts = {}
    for b in SAVED_BOOKS:
        category_counts[b["category"]] = category_counts.get(b["category"], 0) + 1

    st.markdown("""
    <div class="insight-card">
        <div class="insight-icon">📊</div>
        <div class="insight-text"><strong>Your taste profile</strong></div>
    </div>
    """, unsafe_allow_html=True)

    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        pct = int(count / len(SAVED_BOOKS) * 100)
        st.markdown(
            f'<span class="lt-muted" style="font-size:.8rem;">{cat}</span>',
            unsafe_allow_html=True,
        )
        st.markdown(progress_bar(pct), unsafe_allow_html=True)
        st.markdown(
            f'<span class="lt-muted" style="font-size:.72rem;">{pct}% · {count} book{"s" if count>1 else ""}</span>',
            unsafe_allow_html=True,
        )
        spacer(6)

    spacer(16)
    st.markdown('<hr style="border-color:#EBEBEB;">', unsafe_allow_html=True)
    spacer(8)

    # Average rating of saved books
    avg_rating = sum(b["rating"] for b in SAVED_BOOKS) / len(SAVED_BOOKS)
    available_count = sum(1 for b in SAVED_BOOKS if b["status"] == "Available")

    st.markdown(f"""
    <div class="lt-stat" style="margin-bottom:10px;">
        <div class="lt-stat-num">{avg_rating:.1f}</div>
        <div class="lt-stat-label">avg. rating saved</div>
    </div>
    <div class="lt-stat" style="margin-bottom:10px;">
        <div class="lt-stat-num">{available_count}</div>
        <div class="lt-stat-label">available now</div>
    </div>
    """, unsafe_allow_html=True)

    spacer(16)

    # Quick action
    # In production: POST /api/borrowings — borrow all available books at once
    if st.button("📚 Borrow all available", use_container_width=True, type="primary"):
        st.toast(f"Borrowing {available_count} available books!")
        st.balloons()

    spacer(8)

    # In production: GET /api/recommendations?user_id=<id> — refresh list
    if st.button("🔄 Refresh recommendations", use_container_width=True):
        st.toast("Fetching fresh recommendations...")

# =============================================================================
# COMPLETE LIST VIEW (below grid)
# =============================================================================
spacer(24)
st.markdown('<hr style="border-color:#EBEBEB;">', unsafe_allow_html=True)
spacer(8)

section_title("Full reading list")
section_label(f"{len(SAVED_BOOKS)} books · sorted by match score")

for book in SAVED_BOOKS:
    col_cover, col_info, col_rating, col_actions = st.columns([0.5, 3.5, 1.5, 1.5])

    with col_cover:
        spacer(4)
        st.markdown(
            f'<div style="background:{book["color"]};width:52px;height:74px;'
            f'border-radius:6px;position:relative;">'
            f'<div style="position:absolute;left:0;top:0;bottom:0;width:6px;'
            f'background:rgba(0,0,0,0.2);border-radius:6px 0 0 6px;"></div></div>',
            unsafe_allow_html=True,
        )

    with col_info:
        st.markdown(f"""
        <div class="reading-item-title">{book['title']}</div>
        <div class="reading-item-author">{book['author']}</div>
        <div class="reading-item-badge">
            <span class="lt-badge lt-badge-beige"
                  style="font-size:.72rem;">{book['category']}</span>
            <span style="font-size:.72rem;color:#D2B354;margin-left:6px;">
                ✦ {book['match']}
            </span>
            <span class="lt-muted" style="font-size:.72rem;margin-left:8px;">
                Saved {book['saved_date']}
            </span>
        </div>
        """, unsafe_allow_html=True)

    with col_rating:
        spacer(8)
        st.markdown(
            f'<span style="color:#D2B354;font-size:.85rem;">{"★"*int(book["rating"])} {book["rating"]}</span><br>'
            f'<span class="lt-muted" style="font-size:.75rem;">{book["reviews"]} reviews</span>',
            unsafe_allow_html=True,
        )

    with col_actions:
        spacer(4)
        # In production: navigates to /books/<book_id>
        if st.button("View", key=f"view_list_{book['id']}", use_container_width=True):
            st.session_state["selected_book_id"] = book["id"]
            st.toast(f"Opening '{book['title']}'...")

    st.markdown('<hr style="border-color:#F5F5F5;margin:4px 0;">', unsafe_allow_html=True)