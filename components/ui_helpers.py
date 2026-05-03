from html import escape

import streamlit as st


COLORS = {
    "dark_green": "#1F3F2E",
    "mid_green": "#3E7255",
    "light_green": "#DFF2DF",
    "gold": "#D2B354",
    "brown": "#654421",
    "beige": "#EFE5DA",
    "bg": "#FAFAF7",
    "white": "#FFFFFF",
    "text": "#111111",
    "text_muted": "#8A8A8A",
    "text_secondary": "#3A3A3A",
}


def inject_global_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Source+Serif+4:wght@400;500;600&display=swap');

        html, body, [data-testid="stAppViewContainer"] {{
            background-color: {COLORS["bg"]} !important;
            color: {COLORS["text"]} !important;
            font-family: 'Source Serif 4', Georgia, serif !important;
        }}

        #MainMenu, footer, header {{
            visibility: hidden;
        }}

        .block-container {{
            max-width: 1120px !important;
            padding-top: 0rem !important;
            padding-bottom: 2rem !important;
        }}

        .libtrack-navbar {{
            align-items: center;
            background-color: {COLORS["dark_green"]};
            border-radius: 0 0 8px 8px;
            display: flex;
            justify-content: space-between;
            margin-bottom: 0;
            padding: 14px 32px;
            position: sticky;
            top: 0;
            z-index: 999;
        }}

        .logo {{
            align-items: center;
            color: white;
            display: flex;
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 1.3rem;
            font-weight: 700;
            gap: 10px;
        }}

        .logo-icon {{
            align-items: center;
            background-color: {COLORS["gold"]};
            border-radius: 6px;
            color: {COLORS["brown"]};
            display: inline-flex;
            font-size: 0.75rem;
            height: 32px;
            justify-content: center;
            width: 32px;
        }}

        .nav-links {{
            align-items: center;
            display: flex;
            gap: 28px;
        }}

        .nav-link {{
            color: rgba(255,255,255,0.75);
            font-size: 0.9rem;
        }}

        .nav-link.active {{
            color: white;
            font-weight: 600;
        }}

        .nav-search {{
            background: rgba(255,255,255,0.12);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 20px;
            color: rgba(255,255,255,0.65);
            font-size: 0.85rem;
            min-width: 200px;
            padding: 6px 18px;
        }}

        .nav-avatar {{
            align-items: center;
            background-color: {COLORS["gold"]};
            border-radius: 50%;
            color: {COLORS["brown"]};
            display: inline-flex;
            font-weight: 700;
            height: 36px;
            justify-content: center;
            width: 36px;
        }}

        h1, h2, h3 {{
            color: {COLORS["dark_green"]} !important;
            font-family: 'Playfair Display', Georgia, serif !important;
        }}

        .stButton > button {{
            border-radius: 8px !important;
            font-family: 'Source Serif 4', Georgia, serif !important;
            font-size: 0.9rem !important;
        }}

        .badge {{
            border-radius: 20px;
            display: inline-block;
            font-size: 0.78rem;
            font-weight: 500;
            margin-right: 4px;
            padding: 3px 12px;
        }}

        .badge-green, .badge-available {{
            background-color: {COLORS["light_green"]};
            color: {COLORS["dark_green"]};
        }}

        .badge-gold {{
            background-color: {COLORS["gold"]};
            color: {COLORS["brown"]};
        }}

        .badge-beige {{
            background-color: {COLORS["beige"]};
            color: {COLORS["brown"]};
        }}

        .badge-grey {{
            background-color: #F0F0F0;
            color: {COLORS["text_muted"]};
        }}

        .badge-waitlist {{
            background-color: #FEF3CD;
            color: #856404;
        }}

        .book-cover {{
            border-radius: 4px;
            display: inline-block;
            flex-shrink: 0;
            height: 86px;
            width: 60px;
        }}

        .book-cover-lg {{
            border-radius: 6px;
            display: inline-block;
            flex-shrink: 0;
            height: 144px;
            width: 100px;
        }}

        .book-cover-card {{
            border-radius: 6px;
            display: block;
            height: 160px;
            margin-bottom: 8px;
            width: 100%;
        }}

        .card {{
            background: white;
            border: 1px solid #EBEBEB;
            border-radius: 8px;
            margin-bottom: 16px;
            padding: 16px 20px;
        }}

        .avatar, .avatar-lg {{
            align-items: center;
            border-radius: 50%;
            display: inline-flex;
            font-weight: 700;
            justify-content: center;
        }}

        .avatar {{
            font-size: 0.85rem;
            height: 40px;
            width: 40px;
        }}

        .avatar-lg {{
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 1.4rem;
            height: 72px;
            width: 72px;
        }}

        .stars {{
            color: {COLORS["gold"]};
            font-size: 1rem;
            letter-spacing: 1px;
        }}

        .rating-text {{
            color: {COLORS["gold"]};
            font-size: 0.95rem;
            font-weight: 600;
        }}

        .progress-bar-container {{
            background-color: #E8E8E8;
            border-radius: 10px;
            height: 8px;
            margin: 6px 0;
            width: 100%;
        }}

        .progress-bar-fill {{
            background-color: {COLORS["dark_green"]};
            border-radius: 10px;
            height: 8px;
        }}

        .stat-card {{
            background: white;
            border: 1px solid #EBEBEB;
            border-radius: 8px;
            padding: 20px 16px;
            text-align: center;
        }}

        .stat-number {{
            color: {COLORS["dark_green"]};
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 2rem;
            font-weight: 700;
            line-height: 1.1;
        }}

        .stat-label, .muted {{
            color: {COLORS["text_muted"]};
            font-size: 0.85rem;
        }}

        .secondary {{
            color: {COLORS["text_secondary"]};
            font-size: 0.9rem;
        }}

        .section-title {{
            color: {COLORS["dark_green"]};
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 16px;
            margin-top: 8px;
        }}

        .action-row {{
            color: {COLORS["text_muted"]};
            font-size: 0.85rem;
            margin-top: 8px;
        }}

        hr {{
            border: none;
            border-top: 1px solid #EBEBEB;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _session_initials() -> str:
    reader_name = st.session_state.get("reader_name", "")
    words = [part for part in reader_name.split() if part]

    if len(words) == 1:
        return words[0][0].upper()
    if len(words) > 1:
        return "".join(word[0].upper() for word in words[:2])
    return "?"


def render_navbar(active_page: str = ""):
    def nav_class(key: str) -> str:
        return "nav-link active" if active_page == key else "nav-link"

    st.markdown(
        f"""
        <div class="libtrack-navbar">
            <div class="logo">
                <span class="logo-icon">LT</span>
                LibTrack
            </div>
            <div class="nav-links">
                <span class="{nav_class("discover")}">Discover</span>
                <span class="{nav_class("borrowings")}">Borrowings</span>
                <span class="{nav_class("my_library")}">My library</span>
            </div>
            <div style="display:flex; align-items:center; gap:16px;">
                <div class="nav-search">Search for a book...</div>
                <div class="nav-avatar">{escape(_session_initials())}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_book_cover(cover: str | None, size: str = "normal") -> str:
    css_class = "book-cover"
    if size == "large":
        css_class = "book-cover-lg"
    elif size == "card":
        css_class = "book-cover-card"

    cover_value = cover or COLORS["mid_green"]
    if str(cover_value).startswith(("http://", "https://")):
        return (
            f'<img class="{css_class}" src="{escape(str(cover_value))}" '
            f'alt="Book cover" style="object-fit:cover;">'
        )

    return f'<div class="{css_class}" style="background-color:{escape(str(cover_value))};"></div>'


def render_stars(rating: float) -> str:
    safe_rating = max(0, min(5, float(rating or 0)))
    full = int(safe_rating)
    stars = "&#9733;" * full + "&#9734;" * (5 - full)
    return f'<span class="stars">{stars}</span> <span class="rating-text">{safe_rating:.1f}</span>'


def render_badge(label: str, style: str = "green") -> str:
    return f'<span class="badge badge-{style}">{escape(str(label))}</span>'


def render_avatar(initials: str, bg_color: str, text_color: str, size: str = "normal") -> str:
    css_class = "avatar-lg" if size == "large" else "avatar"
    return (
        f'<div class="{css_class}" '
        f'style="background-color:{escape(str(bg_color))}; color:{escape(str(text_color))};">'
        f'{escape(str(initials))}</div>'
    )


def render_progress_bar(percent: int) -> str:
    safe_percent = max(0, min(100, int(percent or 0)))
    return (
        '<div class="progress-bar-container">'
        f'<div class="progress-bar-fill" style="width:{safe_percent}%;"></div>'
        "</div>"
    )


def render_stat_card(number: str, label: str) -> str:
    return (
        '<div class="stat-card">'
        f'<div class="stat-number">{escape(str(number))}</div>'
        f'<div class="stat-label">{escape(str(label))}</div>'
        "</div>"
    )


def page_spacer(px: int = 20):
    st.markdown(f'<div style="height:{int(px)}px;"></div>', unsafe_allow_html=True)


def section_title(text: str):
    st.markdown(f'<div class="section-title">{escape(str(text))}</div>', unsafe_allow_html=True)


def render_sidebar_menu(items: list[str], active: str):
    html = ""
    for item in items:
        cls = "sidebar-item active" if item == active else "sidebar-item"
        html += f'<div class="{cls}">{escape(str(item))}</div>'
    st.markdown(html, unsafe_allow_html=True)
