import streamlit as st
import sys, os

from Backend.Functions.library_data import get_reader_from_session

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
    width: 68px; height: 68px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 2rem; margin: 0 auto 12px; flex-shrink: 0;
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
</style>
""", unsafe_allow_html=True)

spacer(24)

# =============================================================================
# BADGE DEFINITIONS
# =============================================================================
# Each badge has: id, name, description, icon, icon_bg, xp,
#                 earned (bool), progress (0–100), criteria
#
# BADGE OBJECTIVES — the 6 gamified achievements designed for LibTrack:
#
# 1. FIRST CHAPTER    — Borrow your first book              → Engagement
# 2. AVID READER      — Read 10 books total                 → Reading
# 3. STREAK KEEPER    — Read 7 days in a row                → Regularity
# 4. CRITIC'S PEN     — Write 5 reviews                     → Community
# 5. SOCIAL READER    — Get 50 likes on your posts          → Social
# 6. BOOK CLUB HERO   — Comment on 20 community posts       → Social

BADGES = [
    # ── EARNED ───────────────────────────────────────────────────────────
    {
        "id": "first_chapter",
        "name": "First Chapter",
        "description": "Borrow your very first book on LibTrack.",
        "icon": "📖",
        "icon_bg": "#DFF2DF",
        "xp": 50,
        "earned": True,
        "earned_date": "Jan 15, 2024",
        "progress": 100,
        "criteria": "Borrow 1 book",
        "rarity": "Common",
        "rarity_color": "#DFF2DF",
        "rarity_text": "#3E7255",
    },
    {
        "id": "avid_reader",
        "name": "Avid Reader",
        "description": "Read 10 books. Your bookshelf is growing!",
        "icon": "📚",
        "icon_bg": "#DFF2DF",
        "xp": 200,
        "earned": True,
        "earned_date": "Mar 3, 2024",
        "progress": 100,
        "criteria": "Borrow 10 books",
        "rarity": "Uncommon",
        "rarity_color": "#D2B354",
        "rarity_text": "#654421",
    },
    {
        "id": "critics_pen",
        "name": "Critic's Pen",
        "description": "Share your thoughts — write 5 reviews for the community.",
        "icon": "✍️",
        "icon_bg": "#EFE5DA",
        "xp": 150,
        "earned": True,
        "earned_date": "Apr 20, 2024",
        "progress": 100,
        "criteria": "Write 5 reviews",
        "rarity": "Uncommon",
        "rarity_color": "#D2B354",
        "rarity_text": "#654421",
    },
    # ── IN PROGRESS ───────────────────────────────────────────────────────
    {
        "id": "streak_keeper",
        "name": "Streak Keeper",
        "description": "Read every day for 7 consecutive days. Build the habit.",
        "icon": "🔥",
        "icon_bg": "#FFF3CD",
        "xp": 300,
        "earned": False,
        "earned_date": None,
        "progress": 71,   # 5 / 7 days
        "criteria": "7-day reading streak",
        "current": "5 / 7 days",
        "rarity": "Rare",
        "rarity_color": "#EFE5DA",
        "rarity_text": "#654421",
    },
    {
        "id": "social_reader",
        "name": "Social Reader",
        "description": "Your reviews inspire others — collect 50 likes on your posts.",
        "icon": "❤️",
        "icon_bg": "#FBEAF0",
        "xp": 250,
        "earned": False,
        "earned_date": None,
        "progress": 62,   # 31 / 50 likes
        "criteria": "Get 50 likes on posts",
        "current": "31 / 50 likes",
        "rarity": "Rare",
        "rarity_color": "#EFE5DA",
        "rarity_text": "#654421",
    },
    {
        "id": "book_club_hero",
        "name": "Book Club Hero",
        "description": "Be the heart of the community — comment on 20 posts.",
        "icon": "💬",
        "icon_bg": "#E6F1FB",
        "xp": 180,
        "earned": False,
        "earned_date": None,
        "progress": 35,   # 7 / 20 comments
        "criteria": "Comment on 20 posts",
        "current": "7 / 20 comments",
        "rarity": "Common",
        "rarity_color": "#DFF2DF",
        "rarity_text": "#3E7255",
    },
]

# User stats (mock — replace with API)
USER_XP = 400
NEXT_LEVEL_XP = 600
CURRENT_LEVEL = 5
TOTAL_BADGES = sum(1 for b in BADGES if b["earned"])
TOTAL_XP_POSSIBLE = sum(b["xp"] for b in BADGES)

# Reward history log (mock)
HISTORY = [
    {"icon": "📚", "bg": "#DFF2DF", "name": "Avid Reader earned", "date": "Mar 3, 2024", "xp": +200},
    {"icon": "✍️", "bg": "#EFE5DA", "name": "Critic's Pen earned", "date": "Apr 20, 2024", "xp": +150},
    {"icon": "📖", "bg": "#DFF2DF", "name": "First Chapter earned", "date": "Jan 15, 2024", "xp": +50},
    {"icon": "⭐", "bg": "#FFF3CD", "name": "Posted your first review", "date": "Feb 5, 2024", "xp": +20},
    {"icon": "💬", "bg": "#E6F1FB", "name": "First community comment", "date": "Jan 20, 2024", "xp": +10},
]

# XP Leaderboard (mock)
LEADERS = [
    {"rank": 1, "name": "Thomas G.", "init": "TG", "bg": "#D2B354", "col": "#654421", "xp": 1840, "you": False},
    {"rank": 2, "name": "Sophie M.", "init": "SM", "bg": "#EFE5DA", "col": "#654421", "xp": 1320, "you": False},
    {"rank": 3, "name": "Marie L.",  "init": "ML", "bg": "#D2B354", "col": "#654421", "xp": 400,  "you": True},
    {"rank": 4, "name": "Alex C.",   "init": "AC", "bg": "#DFF2DF", "col": "#3E7255", "xp": 310,  "you": False},
]

# =============================================================================
# XP / LEVEL HERO BANNER
# =============================================================================
xp_pct = int(USER_XP / NEXT_LEVEL_XP * 100)
earned_badges = [b for b in BADGES if b["earned"]]
locked_badges  = [b for b in BADGES if not b["earned"]]

st.markdown(f"""
<div class="xp-hero">
    <div style="display:flex;align-items:center;gap:28px;flex-wrap:wrap;">
        <div class="xp-level-ring">
            <div class="xp-level-num">{CURRENT_LEVEL}</div>
            <div class="xp-level-lbl">Level</div>
        </div>
        <div class="xp-info">
            <h2>Your Rewards</h2>
            <p class="sub">
                {TOTAL_BADGES} badges earned · {USER_XP} XP total
            </p>
            <div class="xp-bar-bg">
                <div class="xp-bar-fill" style="width:{xp_pct}%;"></div>
            </div>
            <div class="xp-bar-labels">
                <span>{USER_XP} XP</span>
                <span>Level {CURRENT_LEVEL + 1} at {NEXT_LEVEL_XP} XP</span>
            </div>
        </div>
        <div style="text-align:center;flex-shrink:0;">
            <div style="font-family:'Playfair Display',serif;font-size:2rem;
                        font-weight:700;color:#D2B354;line-height:1;">
                {TOTAL_BADGES}/{len(BADGES)}
            </div>
            <div style="font-size:0.72rem;color:rgba(255,255,255,0.5);
                        text-transform:uppercase;letter-spacing:.1em;">
                badges
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# MAIN LAYOUT: badges (left 2/3) + sidebar (right 1/3)
# =============================================================================
main_col, side_col = st.columns([2.5, 1])

with main_col:

    # ── EARNED BADGES ─────────────────────────────────────────────────────
    section_title(f"Earned badges · {len(earned_badges)}")
    section_label("Tap a badge to see details")

    earned_cols = st.columns(3)
    for i, b in enumerate(earned_badges):
        with earned_cols[i % 3]:
            st.markdown(f"""
            <div class="badge-card">
                <div class="badge-earned-tag">✓ Earned · {b['earned_date']}</div>
                <div class="badge-icon-wrap" style="background:{b['icon_bg']};">
                    {b['icon']}
                </div>
                <div class="badge-name">{b['name']}</div>
                <div class="badge-desc">{b['description']}</div>
                <span class="lt-badge" style="background:{b['rarity_color']};
                      color:{b['rarity_text']};font-size:.7rem;margin-right:4px;">
                    {b['rarity']}
                </span>
                <span class="badge-xp">+{b['xp']} XP</span>
            </div>
            """, unsafe_allow_html=True)
            spacer(10)

    spacer(24)
    st.markdown('<hr style="border-color:#EBEBEB;">', unsafe_allow_html=True)

    # ── LOCKED BADGES — with progress ────────────────────────────────────
    section_title(f"In progress · {len(locked_badges)}")
    section_label("Keep reading to unlock these badges")

    locked_cols = st.columns(3)
    for i, b in enumerate(locked_badges):
        with locked_cols[i % 3]:
            current_label = b.get("current", f"{b['progress']}%")
            st.markdown(f"""
            <div class="badge-card locked">
                <div class="badge-icon-wrap"
                     style="background:#F0F0F0;filter:grayscale(0.4);">
                    {b['icon']}
                </div>
                <div class="badge-name" style="color:#8A8A8A;">{b['name']}</div>
                <div class="badge-desc">{b['description']}</div>
                <div style="width:100%;margin:8px 0 4px;">
                    <div style="background:#E8E8E8;border-radius:8px;height:6px;">
                        <div style="background:#3E7255;border-radius:8px;
                             height:6px;width:{b['progress']}%;"></div>
                    </div>
                    <div style="display:flex;justify-content:space-between;
                         margin-top:4px;font-size:.7rem;color:#8A8A8A;">
                        <span>{current_label}</span>
                        <span>{b['progress']}%</span>
                    </div>
                </div>
                <span class="lt-badge" style="background:{b['rarity_color']};
                      color:{b['rarity_text']};font-size:.7rem;margin-right:4px;">
                    {b['rarity']}
                </span>
                <span class="badge-locked-xp">+{b['xp']} XP</span>
            </div>
            """, unsafe_allow_html=True)
            spacer(10)

    spacer(24)
    st.markdown('<hr style="border-color:#EBEBEB;">', unsafe_allow_html=True)

    # ── REWARD HISTORY ────────────────────────────────────────────────────
    section_title("Reward history")

    for h in HISTORY:
        xp_display = f"+{h['xp']} XP"
        st.markdown(f"""
        <div class="history-item">
            <div class="history-icon" style="background:{h['bg']};">{h['icon']}</div>
            <div class="history-info">
                <div class="history-name">{h['name']}</div>
                <div class="history-date">{h['date']}</div>
            </div>
            <div class="history-xp">{xp_display}</div>
        </div>
        """, unsafe_allow_html=True)


# ── SIDEBAR ────────────────────────────────────────────────────────────────
with side_col:
    spacer(4)

    # All 6 badge objectives explained
    section_title("Badge objectives")
    section_label("How to earn each badge")

    objectives = [
        ("📖", "First Chapter",    "Borrow your 1st book",            "50 XP"),
        ("📚", "Avid Reader",      "Borrow 10 books total",           "200 XP"),
        ("✍️", "Critic's Pen",     "Write 5 reviews",                 "150 XP"),
        ("🔥", "Streak Keeper",    "Read 7 days in a row",            "300 XP"),
        ("❤️", "Social Reader",    "Get 50 likes on your posts",      "250 XP"),
        ("💬", "Book Club Hero",   "Comment on 20 community posts",   "180 XP"),
    ]

    for icon, name, how, xp in objectives:
        earned = any(b["name"] == name and b["earned"] for b in BADGES)
        check = "✓ " if earned else ""
        color = COLORS["dark_green"] if earned else COLORS["muted"]
        st.markdown(f"""
        <div style="display:flex;align-items:flex-start;gap:10px;
             padding:8px 0;border-bottom:1px solid #F5F5F5;">
            <span style="font-size:1.2rem;flex-shrink:0;">{icon}</span>
            <div style="flex:1;">
                <div style="font-size:.85rem;font-weight:600;color:{color};">
                    {check}{name}
                </div>
                <div style="font-size:.75rem;color:#8A8A8A;">{how}</div>
            </div>
            <div style="font-size:.72rem;color:#D2B354;font-weight:700;
                 flex-shrink:0;">{xp}</div>
        </div>
        """, unsafe_allow_html=True)

    spacer(20)
    st.markdown('<hr style="border-color:#EBEBEB;">', unsafe_allow_html=True)

    # XP Leaderboard
    section_title("XP leaderboard")
    for l in LEADERS:
        you_tag = ' <span style="font-size:.7rem;color:#D2B354;">(you)</span>' if l["you"] else ""
        rank_color = "#D2B354" if l["rank"] == 1 else (COLORS["muted"] if l["rank"] == 2 else COLORS["secondary"])
        st.markdown(f"""
        <div class="leader-row">
            <div class="leader-rank" style="color:{rank_color};">{l['rank']}</div>
            <div class="leader-av" style="background:{l['bg']};color:{l['col']};">
                {l['init']}
            </div>
            <div class="leader-info">
                <div class="leader-name">{l['name']}{you_tag}</div>
                <div class="leader-xp">{l['xp']:,} XP</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    spacer(16)

    # Progress toward next level
    st.markdown(f"""
    <div class="lt-stat">
        <div style="font-size:.72rem;color:#8A8A8A;text-transform:uppercase;
             letter-spacing:.1em;margin-bottom:8px;">Next level</div>
        <div style="background:#E8E8E8;border-radius:8px;height:8px;margin-bottom:6px;">
            <div style="background:#D2B354;border-radius:8px;
                 height:8px;width:{xp_pct}%;"></div>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:.78rem;">
            <span style="color:#1F3F2E;font-weight:600;">{USER_XP} XP</span>
            <span style="color:#8A8A8A;">{NEXT_LEVEL_XP} XP</span>
        </div>
        <div style="font-size:.75rem;color:#8A8A8A;margin-top:6px;">
            {NEXT_LEVEL_XP - USER_XP} XP to reach Level {CURRENT_LEVEL + 1}
        </div>
    </div>
    """, unsafe_allow_html=True)

    page_spacer(20)
    # --------------------------------------------------------------------NAVIGATION
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    section_title("Navigation")
    render_navigation_section()