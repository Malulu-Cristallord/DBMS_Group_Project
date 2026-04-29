# =============================================================================
# FILE: components/ui_helpers.py
# PURPOSE: Shared UI helpers, CSS injection, and utility functions.
#          All custom styling lives here so every page uses the same
#          visual identity (colors, fonts, buttons, badges, cards, etc.)
# =============================================================================

import streamlit as st


# =============================================================================
# COLOR PALETTE (matches the LibTrack design system)
# =============================================================================
COLORS = {
    "dark_green":   "#1F3F2E",   # Navbar, main buttons, headings
    "mid_green":    "#3E7255",   # Book covers, secondary highlights
    "light_green":  "#DFF2DF",   # Active sidebar items, soft badges
    "gold":         "#D2B354",   # Avatars, ratings, premium badges
    "brown":        "#654421",   # Earthy accents, some covers
    "beige":        "#EFE5DA",   # Physical tags, neutral badges
    "bg":           "#FAFAF7",   # Page background
    "white":        "#FFFFFF",
    "text":         "#111111",
    "text_muted":   "#8A8A8A",
    "text_secondary": "#3A3A3A",
}


def inject_global_css():
    """
    Inject global CSS into the Streamlit app.
    This function must be called at the top of EVERY page to ensure
    consistent styling. It sets fonts, colors, button styles, and layout.
    """
    st.markdown(f"""
    <style>
    /* =========================================================
       IMPORT SERIF FONT (book/editorial feel)
       ========================================================= */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Source+Serif+4:wght@300;400;500;600&display=swap');

    /* =========================================================
       GLOBAL RESET & BASE
       ========================================================= */
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: {COLORS['bg']} !important;
        font-family: 'Source Serif 4', Georgia, serif !important;
        color: {COLORS['text']} !important;
    }}

    /* Hide default Streamlit header and footer */
    #MainMenu, footer, header {{
        visibility: hidden;
    }}

    /* Remove top padding from main container */
    .block-container {{
        padding-top: 0rem !important;
        padding-bottom: 2rem !important;
        max-width: 1100px !important;
    }}

    /* =========================================================
       NAVBAR STYLES
       ========================================================= */
    .libtrack-navbar {{
        background-color: {COLORS['dark_green']};
        padding: 14px 32px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0px;
        border-radius: 0 0 8px 8px;
        position: sticky;
        top: 0;
        z-index: 999;
    }}
    .libtrack-navbar .logo {{
        display: flex;
        align-items: center;
        gap: 10px;
        color: white;
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1.3rem;
        font-weight: 700;
        text-decoration: none;
    }}
    .libtrack-navbar .logo-icon {{
        background-color: {COLORS['gold']};
        width: 32px;
        height: 32px;
        border-radius: 6px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
    }}
    .nav-links {{
        display: flex;
        gap: 28px;
        align-items: center;
    }}
    .nav-link {{
        color: rgba(255,255,255,0.75);
        text-decoration: none;
        font-size: 0.9rem;
        font-family: 'Source Serif 4', Georgia, serif;
        transition: color 0.2s;
        cursor: pointer;
    }}
    .nav-link:hover, .nav-link.active {{
        color: white;
    }}
    .nav-search {{
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 20px;
        padding: 6px 18px;
        color: rgba(255,255,255,0.6);
        font-size: 0.85rem;
        min-width: 200px;
    }}
    .nav-avatar {{
        background-color: {COLORS['gold']};
        color: {COLORS['brown']};
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.85rem;
        font-family: 'Source Serif 4', Georgia, serif;
        cursor: pointer;
    }}

    /* =========================================================
       HEADINGS
       ========================================================= */
    h1, h2, h3 {{
        font-family: 'Playfair Display', Georgia, serif !important;
        color: {COLORS['dark_green']} !important;
    }}
    h1 {{ font-size: 2rem !important; font-weight: 700 !important; }}
    h2 {{ font-size: 1.4rem !important; font-weight: 600 !important; }}
    h3 {{ font-size: 1.1rem !important; font-weight: 600 !important; }}

    /* =========================================================
       BUTTONS - Primary (dark green)
       ========================================================= */
    .btn-primary {{
        background-color: {COLORS['dark_green']};
        color: white;
        border: none;
        padding: 10px 22px;
        border-radius: 8px;
        font-size: 0.9rem;
        font-family: 'Source Serif 4', Georgia, serif;
        cursor: pointer;
        font-weight: 500;
        transition: opacity 0.2s;
        display: inline-block;
        text-align: center;
    }}
    .btn-primary:hover {{ opacity: 0.88; }}

    /* =========================================================
       BUTTONS - Secondary (outlined)
       ========================================================= */
    .btn-secondary {{
        background-color: white;
        color: {COLORS['dark_green']};
        border: 1.5px solid {COLORS['dark_green']};
        padding: 9px 20px;
        border-radius: 8px;
        font-size: 0.9rem;
        font-family: 'Source Serif 4', Georgia, serif;
        cursor: pointer;
        font-weight: 500;
        display: inline-block;
        text-align: center;
    }}

    /* =========================================================
       STREAMLIT NATIVE BUTTON OVERRIDES
       ========================================================= */
    .stButton > button {{
        font-family: 'Source Serif 4', Georgia, serif !important;
        border-radius: 8px !important;
        font-size: 0.9rem !important;
        padding: 0.45rem 1.2rem !important;
        transition: all 0.2s !important;
    }}

    /* =========================================================
       BADGES / PILLS
       ========================================================= */
    .badge {{
        display: inline-block;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 500;
        font-family: 'Source Serif 4', Georgia, serif;
        margin-right: 4px;
    }}
    .badge-green {{
        background-color: {COLORS['light_green']};
        color: {COLORS['dark_green']};
    }}
    .badge-gold {{
        background-color: {COLORS['gold']};
        color: {COLORS['brown']};
    }}
    .badge-beige {{
        background-color: {COLORS['beige']};
        color: {COLORS['brown']};
    }}
    .badge-grey {{
        background-color: #F0F0F0;
        color: {COLORS['text_muted']};
    }}
    .badge-available {{
        background-color: {COLORS['light_green']};
        color: {COLORS['dark_green']};
    }}
    .badge-waitlist {{
        background-color: #FEF3CD;
        color: #856404;
    }}

    /* =========================================================
       BOOK COVER PLACEHOLDER
       ========================================================= */
    .book-cover {{
        width: 60px;
        height: 86px;
        border-radius: 4px;
        display: inline-block;
        flex-shrink: 0;
    }}
    .book-cover-lg {{
        width: 100px;
        height: 144px;
        border-radius: 6px;
        display: inline-block;
        flex-shrink: 0;
    }}
    .book-cover-card {{
        width: 100%;
        height: 160px;
        border-radius: 6px;
        display: block;
        margin-bottom: 8px;
    }}

    /* =========================================================
       CARD CONTAINERS
       ========================================================= */
    .card {{
        background: white;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 16px;
        border: 1px solid #EBEBEB;
    }}
    .card:hover {{
        border-color: {COLORS['mid_green']};
    }}

    /* =========================================================
       AVATAR CIRCLE
       ========================================================= */
    .avatar {{
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.85rem;
        font-family: 'Source Serif 4', Georgia, serif;
    }}
    .avatar-lg {{
        width: 72px;
        height: 72px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1.4rem;
        font-family: 'Playfair Display', Georgia, serif;
    }}

    /* =========================================================
       SIDEBAR MENU ITEMS
       ========================================================= */
    .sidebar-item {{
        padding: 10px 16px;
        border-radius: 6px;
        margin-bottom: 4px;
        font-size: 0.95rem;
        font-family: 'Source Serif 4', Georgia, serif;
        cursor: pointer;
        color: {COLORS['text']};
    }}
    .sidebar-item.active {{
        background-color: {COLORS['light_green']};
        color: {COLORS['dark_green']};
        border-left: 3px solid {COLORS['dark_green']};
        font-weight: 600;
    }}

    /* =========================================================
       STAR RATING
       ========================================================= */
    .stars {{
        color: {COLORS['gold']};
        font-size: 1rem;
        letter-spacing: 1px;
    }}
    .rating-text {{
        color: {COLORS['gold']};
        font-weight: 600;
        font-size: 0.95rem;
    }}

    /* =========================================================
       SECTION DIVIDER
       ========================================================= */
    .section-divider {{
        border: none;
        border-top: 1px solid #EBEBEB;
        margin: 20px 0;
    }}

    /* =========================================================
       PROGRESS BAR
       ========================================================= */
    .progress-bar-container {{
        background-color: #E8E8E8;
        border-radius: 10px;
        height: 8px;
        width: 100%;
        margin: 6px 0;
    }}
    .progress-bar-fill {{
        background-color: {COLORS['dark_green']};
        border-radius: 10px;
        height: 8px;
    }}

    /* =========================================================
       STAT CARD
       ========================================================= */
    .stat-card {{
        background: white;
        border: 1px solid #EBEBEB;
        border-radius: 10px;
        padding: 20px 16px;
        text-align: center;
    }}
    .stat-number {{
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 2rem;
        font-weight: 700;
        color: {COLORS['dark_green']};
        line-height: 1.1;
    }}
    .stat-label {{
        font-size: 0.82rem;
        color: {COLORS['text_muted']};
        margin-top: 4px;
        font-family: 'Source Serif 4', Georgia, serif;
    }}

    /* =========================================================
       INPUT FIELDS
       ========================================================= */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {{
        border-radius: 8px !important;
        border-color: #DCDCDC !important;
        font-family: 'Source Serif 4', Georgia, serif !important;
    }}
    .stSelectbox > div > div {{
        border-radius: 8px !important;
        font-family: 'Source Serif 4', Georgia, serif !important;
    }}

    /* =========================================================
       PAGE SECTION TITLE
       ========================================================= */
    .section-title {{
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 1.25rem;
        font-weight: 600;
        color: {COLORS['dark_green']};
        margin-bottom: 16px;
        margin-top: 8px;
    }}

    /* =========================================================
       MUTED HELPER TEXT
       ========================================================= */
    .muted {{
        color: {COLORS['text_muted']};
        font-size: 0.85rem;
    }}
    .secondary {{
        color: {COLORS['text_secondary']};
        font-size: 0.9rem;
    }}

    /* Post card action row */
    .action-row {{
        color: {COLORS['text_muted']};
        font-size: 0.85rem;
        margin-top: 8px;
    }}

    /* Horizontal rule */
    hr {{
        border: none;
        border-top: 1px solid #EBEBEB;
    }}

    /* =========================================================
       FORM / LOGIN CARD
       ========================================================= */
    .form-card {{
        background: white;
        border-radius: 14px;
        padding: 40px 48px;
        border: 1px solid #EBEBEB;
        max-width: 480px;
        margin: 0 auto;
    }}

    </style>
    """, unsafe_allow_html=True)


def render_navbar(active_page: str = ""):
    """
    Render the LibTrack top navigation bar.
    active_page: One of 'discover', 'borrowings', 'my_library'
    This HTML block simulates the navbar. In production, navigation
    would use server-side routing or a JS framework.
    """
    pages = {
        "discover":    "2_Discovery",
        "borrowings":  "4_Borrowings",
        "my_library":  "6_Reading_History",
    }

    def _cls(key):
        return "nav-link active" if active_page == key else "nav-link"

    st.markdown(f"""
    <div class="libtrack-navbar">
        <div class="logo">
            <span class="logo-icon">📖</span>
            LibTrack
        </div>
        <div class="nav-links">
            <span class="{_cls('discover')}">Discover</span>
            <span class="{_cls('borrowings')}">Borrowings</span>
            <span class="{_cls('my_library')}">My library</span>
        </div>
        <div style="display:flex; align-items:center; gap:16px;">
            <div class="nav-search">Search for a book...</div>
            <div class="nav-avatar">ML</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_book_cover(color: str, size: str = "normal") -> str:
    """
    Return an HTML string for a colored book cover placeholder.
    size: 'normal' (60x86px), 'large' (100x144px), 'card' (full-width, 160px high)
    In production: replace with <img src="..." /> using the real book cover URL.
    """
    if size == "large":
        css_class = "book-cover-lg"
    elif size == "card":
        css_class = "book-cover-card"
    else:
        css_class = "book-cover"

    return f'<div class="{css_class}" style="background-color:{color};"></div>'


def render_stars(rating: float) -> str:
    """
    Return HTML star rating display.
    rating: float between 0 and 5
    """
    full = int(rating)
    stars = "★" * full + "☆" * (5 - full)
    return f'<span class="stars">{stars}</span> <span class="rating-text">{rating}</span>'


def render_badge(label: str, style: str = "green") -> str:
    """
    Return HTML for a badge pill.
    style: 'green', 'gold', 'beige', 'grey'
    """
    return f'<span class="badge badge-{style}">{label}</span>'


def render_avatar(initials: str, bg_color: str, text_color: str, size: str = "normal") -> str:
    """
    Return HTML for a circular avatar with initials.
    size: 'normal' (40px) or 'large' (72px)
    """
    css_class = "avatar-lg" if size == "large" else "avatar"
    return (
        f'<div class="{css_class}" '
        f'style="background-color:{bg_color}; color:{text_color};">'
        f'{initials}</div>'
    )


def render_progress_bar(percent: int) -> str:
    """Return HTML for a custom progress bar (0–100)."""
    return f"""
    <div class="progress-bar-container">
        <div class="progress-bar-fill" style="width:{percent}%;"></div>
    </div>
    """


def render_stat_card(number: str, label: str) -> str:
    """Return HTML for a simple statistics card."""
    return f"""
    <div class="stat-card">
        <div class="stat-number">{number}</div>
        <div class="stat-label">{label}</div>
    </div>
    """


def page_spacer(px: int = 20):
    """Add vertical spacing between elements."""
    st.markdown(f'<div style="height:{px}px;"></div>', unsafe_allow_html=True)


def section_title(text: str):
    """Render a styled section heading."""
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)


def render_sidebar_menu(items: list, active: str):
    """
    Render a sidebar vertical menu.
    items: list of strings (menu labels)
    active: the currently active item label
    """
    html = ""
    for item in items:
        cls = "sidebar-item active" if item == active else "sidebar-item"
        html += f'<div class="{cls}">{item}</div>'
    st.markdown(html, unsafe_allow_html=True)