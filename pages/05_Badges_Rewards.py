import streamlit as st
import base64
import sys, os
from html import escape
from Backend.Functions.library_data import get_reader_from_session, get_reader_badges, get_reader_locked_badges

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.ui_helpers import (
    inject_global_css, render_navbar,
    badge, progress_bar,
    section_title, section_label, spacer, COLORS, render_login_required, page_spacer, render_navigation_section,
)

st.set_page_config(
    page_title="Badges & Rewards — LibTrack",
    page_icon="🏅",
    layout="wide",
    initial_sidebar_state="collapsed"
)
inject_global_css()
render_navbar("Badges")
current_reader = get_reader_from_session(st.session_state)
if current_reader is None:
    render_login_required("Please sign in before writing a review.")
    st.stop()
# ── Page-specific CSS ─────────────────────────────────────────────────────
st.markdown("""
<style>
/* XP / level hero */
.xp-hero {
    background: #1F3F2E;
    border-radius: 16px; padding: 36px 36px 32px;
    margin-bottom: 36px; position: relative; overflow: hidden;
}
.xp-hero::before {
    content: ''; position: absolute; right: -80px; top: -80px;
    width: 300px; height: 300px; border-radius: 50%;
    background: rgba(210,179,84,0.12); pointer-events: none;
}
.xp-level-ring {
    width: 90px; height: 90px; border-radius: 50%;
    border: 4px solid #D2B354;
    display: flex; align-items: center; justify-content: center;
    flex-direction: column; flex-shrink: 0;
}
.xp-level-num {
    font-family: 'Playfair Display', serif;
    font-size: 2rem; font-weight: 700; color: #D2B354; line-height: 1;
}
.xp-level-lbl { font-size: 0.6rem; color: rgba(255,255,255,0.5);
    text-transform: uppercase; letter-spacing: .1em; }
.xp-info { flex: 1; }
.xp-info h2 {
    font-family: 'Playfair Display', serif !important;
    color: white !important; font-size: 1.5rem !important;
    margin-bottom: 4px !important;
}
.xp-info .sub { color: rgba(255,255,255,0.6); font-size: 0.85rem; margin-bottom: 14px; }
.xp-bar-bg { background: rgba(255,255,255,0.15); border-radius: 8px; height: 10px; margin-bottom: 6px; }
.xp-bar-fill { background: #D2B354; border-radius: 8px; height: 10px; }
.xp-bar-labels { display: flex; justify-content: space-between;
    font-size: 0.72rem; color: rgba(255,255,255,0.5); }

/* Badge card — earned */
.badge-card {
    background: white; border-radius: 14px;
    border: 1px solid #EBEBEB; padding: 24px 16px;
    text-align: center; transition: all .25s; cursor: default;
    min-height: 200px; display: flex; flex-direction: column;
    align-items: center; justify-content: center;
}
.badge-card:hover {
    border-color: #D2B354;
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(210,179,84,0.15);
}
.badge-card.locked {
    opacity: 0.5; cursor: not-allowed;
}
.badge-card.locked:hover {
    border-color: #EBEBEB;
    transform: none;
    box-shadow: none;
}
.badge-icon-wrap {
    width: 68px;
    height: 68px;
    border-radius: 50%;
    background: #F7F7F7;

    display: flex;
    align-items: center;
    justify-content: center;

    margin: 0 auto 12px;
    flex-shrink: 0;

    overflow: hidden;
}

.badge-icon-wrap img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 50%;
}
.badge-name {
    font-family: 'Playfair Display', serif;
    font-size: 0.95rem; font-weight: 600; color: #1F3F2E;
    margin-bottom: 4px;
}
.badge-desc { font-size: 0.75rem; color: #8A8A8A; line-height: 1.45; margin-bottom: 10px; }
.badge-xp {
    display: inline-block; padding: 3px 10px;
    background: #DFF2DF; color: #1F3F2E;
    border-radius: 20px; font-size: 0.7rem; font-weight: 700;
}
.badge-locked-xp {
    display: inline-block; padding: 3px 10px;
    background: #F0F0F0; color: #AAAAAA;
    border-radius: 20px; font-size: 0.7rem; font-weight: 700;
}
.badge-earned-tag {
    display: inline-block; padding: 3px 10px;
    background: #D2B354; color: #654421;
    border-radius: 20px; font-size: 0.68rem; font-weight: 700;
    margin-bottom: 8px;
}

/* History log */
.history-item {
    display: flex; align-items: center; gap: 14px;
    padding: 12px 0; border-bottom: 1px solid #F5F5F5;
}
.history-icon {
    width: 38px; height: 38px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem; flex-shrink: 0;
}
.history-info { flex: 1; }
.history-name { font-size: 0.88rem; font-weight: 600; color: #1F3F2E; margin-bottom: 2px; }
.history-date { font-size: 0.75rem; color: #8A8A8A; }
.history-xp {
    font-family: 'Playfair Display', serif;
    font-size: 1rem; font-weight: 700; color: #D2B354;
    flex-shrink: 0;
}

/* XP leaderboard */
.leader-row {
    display: flex; align-items: center; gap: 14px;
    padding: 10px 0; border-bottom: 1px solid #F5F5F5;
}
.leader-rank { font-family: 'Playfair Display', serif;
    font-size: 1.1rem; color: #8A8A8A; font-weight: 700; width: 24px; }
.leader-av { width: 36px; height: 36px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 0.8rem; flex-shrink: 0; }
.leader-info { flex: 1; }
.leader-name { font-size: 0.88rem; font-weight: 600; color: #1F3F2E; }
.leader-xp { font-size: 0.75rem; color: #8A8A8A; }
/* More */
/* Locked badge progress summary */
.progress-summary {
    background: linear-gradient(135deg, #F8FAF8 0%, #EEF5EE 100%);
    border: 1px solid #E3ECE3;
    border-radius: 16px;
    padding: 18px 20px;
    margin: 10px 0 22px;
}

.progress-summary-title {
    display: flex;
    align-items: center;
    gap: 10px;

    font-family: 'Playfair Display', serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: #1F3F2E;

    margin-bottom: 14px;
}

.progress-summary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 14px;
}

.progress-stat {
    background: rgba(255,255,255,0.75);
    border: 1px solid #E8ECE8;
    border-radius: 12px;
    padding: 14px 16px;
}

.progress-stat-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: .08em;
    color: #7B8B7B;
    margin-bottom: 6px;
    font-weight: 700;
}

.progress-stat-value {
    font-family: 'Playfair Display', serif;
    font-size: 1.35rem;
    font-weight: 700;
    color: #1F3F2E;
    line-height: 1;
}

.progress-summary-footer {
    margin-top: 14px;
    padding-top: 12px;
    border-top: 1px dashed #D6DFD6;

    font-size: 0.82rem;
    color: #6E7C6E;

    display: flex;
    align-items: center;
    gap: 8px;
}
</style>
""", unsafe_allow_html=True)

spacer(24)


# User stats (mock — replace with API)
reader_points = current_reader["Points"]
print(reader_points)
earned_badges = get_reader_badges(current_reader["Reader_ID"])
locked_badges = get_reader_locked_badges(current_reader["Reader_ID"])
book_read = earned_badges[0]["Books_Read"] if earned_badges else 0

def image_to_base64(image_path: str) -> str:
    """
    Convert local image file to base64 string.
    Returns empty string if file does not exist.
    """

    if not image_path:
        return ""

    if not os.path.exists(image_path):
        print(f"Missing image: {image_path}")
        return ""

    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()

    return encoded
# =============================================================================
# MAIN LAYOUT: badges (left 2/3) + sidebar (right 1/3)
# =============================================================================
# ── EARNED BADGES ─────────────────────────────────────────────────────
section_title(f"Earned badges · {len(earned_badges)}")

earned_cols = st.columns(3)
for i, b in enumerate(earned_badges):
    img64 = image_to_base64(b["Badge_Image_Path"])
    with earned_cols[i % 3]:
        st.markdown(f"""
        <div class="badge-card">
            <div class="badge-earned-tag">✓ Earned · {b['Given_Time']}</div>
            <div class="badge-icon-wrap">
                <img src="data:image/png;base64,{img64}", alt="This is an image of the badge">
            </div>
            <div class="badge-name">{b['Badge_Name']}</div>
            <div class="badge-desc">{b['Badge_Description']}</div>
            <span class="lt-badge"font-size:.7rem;margin-right:4px;">
                {b['Badge_Rarity']}
            </span>
            <span class="badge-xp">+{b['Badge_Points']} Points</span>
        </div>
        """, unsafe_allow_html=True)
        spacer(10)

spacer(24)
st.markdown('<hr style="border-color:#EBEBEB;">', unsafe_allow_html=True)

# ── LOCKED BADGES — with progress ────────────────────────────────────
section_title(f"In progress · {len(locked_badges)}")
st.markdown(f"""
<div class="progress-summary">
    <div class="progress-summary-title">
        🔒 Badge Progress Overview
    </div>
    <div class="progress-summary-grid">
        <div class="progress-stat">
            <div class="progress-stat-label">
                Current Points
            </div>
            <div class="progress-stat-value">
                {reader_points}
            </div>
        </div>
        <div class="progress-stat">
            <div class="progress-stat-label">
                Reading Sessions
            </div>
            <div class="progress-stat-value">
                {book_read}
            </div>
        </div>
        <div class="progress-stat">
            <div class="progress-stat-label">
                Locked Badges
            </div>
            <div class="progress-stat-value">
                {len(locked_badges)}
            </div>
        </div>
    </div>
    <div class="progress-summary-footer">
        ✨ Keep reading consistently to unlock more achievements.
    </div>
</div>
""", unsafe_allow_html=True)

locked_cols = st.columns(3)
for i, b in enumerate(locked_badges):
    img64 = image_to_base64(b["Badge_Image_Path"])
    with locked_cols[i % 3]:
        st.markdown(f"""
        <div class="badge-card locked">
            <div class="badge-icon-wrap"
                 style="background:#F0F0F0;filter:grayscale(0.4);">
                 <img src="data:image/png;base64,{img64}", alt="This is an image of the badge">
            </div>
            <div class="badge-name" style="color:#8A8A8A;">{b['Badge_Name']}</div>
            <div class="badge-desc">{b['Badge_Description']}</div>
            <div style="width:100%;margin:8px 0 4px;">
                <div style="background:#E8E8E8;border-radius:8px;height:6px;">
                </div>
                <div style="display:flex;justify-content:space-between;
                     margin-top:4px;font-size:.7rem;color:#8A8A8A;">
                </div>
            </div>
            <span class="lt-badge" style=font-size:.7rem;margin-right:4px;">
                {b['Badge_Rarity']}
            </span>
            <span class="badge-locked-xp">+{b['Badge_Points']} XP</span>
        </div>
        """, unsafe_allow_html=True)
        spacer(10)

spacer(24)
st.markdown('<hr style="border-color:#EBEBEB;">', unsafe_allow_html=True)
# --------------------------------------------------------------------NAVIGATION
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
section_title("Navigation")
render_navigation_section()