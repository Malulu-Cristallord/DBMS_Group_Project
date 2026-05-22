# =============================================================================
# FILE: pages/04_Record_Reading.py
# PURPOSE: "Record Reading" — Real-time reading timer, session logging,
#          and Apple Health-style reading trend dashboard.
#
# FRONT-END ONLY. Timer runs in-session only (no persistence).
#
# FUTURE BACK-END INTEGRATION:
#   - Save session: POST /api/reading-sessions { book_id, duration_min, date }
#   - Get history:  GET  /api/reading-sessions?user_id=<id>&period=week
#   - Get trends:   GET  /api/stats/reading-time?user_id=<id>&view=month
#   - Current book: GET  /api/borrowings?user_id=<id>&status=active
# =============================================================================

import streamlit as st
import time
import datetime
import sys, os

from Backend.Functions.library_data import get_reader_from_session

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.ui_helpers import (
    inject_global_css, render_navbar,
    section_title, section_label, spacer, COLORS, COVER_COLORS, render_login_required, render_navigation_section,
    page_spacer,
)

st.set_page_config(
    page_title="Record Reading — LibTrack",
    page_icon="⏱️",
    layout="wide",
)
inject_global_css()
render_navbar("Record Reading")

current_reader = get_reader_from_session(st.session_state)
if current_reader is None:
    render_login_required("Please sign in before writing a review.")
    st.stop()

# ── Page-specific CSS ─────────────────────────────────────────────────────
st.markdown("""
<style>
/* Timer card */
.timer-card {
    background: #1F3F2E;
    border-radius: 20px; padding: 44px 36px;
    text-align: center; position: relative; overflow: hidden;
}
.timer-card::before {
    content: ''; position: absolute; right: -60px; top: -60px;
    width: 260px; height: 260px; border-radius: 50%;
    background: rgba(210,179,84,0.1); pointer-events: none;
}
.timer-card::after {
    content: ''; position: absolute; left: -40px; bottom: -60px;
    width: 180px; height: 180px; border-radius: 50%;
    background: rgba(255,255,255,0.04); pointer-events: none;
}
.timer-display {
    font-family: 'Playfair Display', serif;
    font-size: 5.5rem; font-weight: 700; color: white;
    letter-spacing: 6px; line-height: 1; margin-bottom: 8px;
    position: relative; z-index: 1;
}
.timer-sub {
    font-size: 0.75rem; letter-spacing: 0.15em; text-transform: uppercase;
    color: rgba(255,255,255,0.45); margin-bottom: 28px; position: relative; z-index: 1;
}
.timer-book-name {
    color: #D2B354; font-size: 1rem; font-style: italic;
    font-family: 'Playfair Display', serif;
    margin-bottom: 28px; position: relative; z-index: 1;
}
.timer-btns {
    display: flex; gap: 12px; justify-content: center;
    position: relative; z-index: 1;
}
.timer-btn-primary {
    background: #D2B354; color: #654421; border: none;
    padding: 12px 32px; border-radius: 10px; font-size: 1rem;
    font-family: 'Source Serif 4', serif; font-weight: 600;
    cursor: pointer; transition: opacity .2s;
}
.timer-btn-primary:hover { opacity: 0.88; }
.timer-btn-secondary {
    background: rgba(255,255,255,0.12); color: white;
    border: 1.5px solid rgba(255,255,255,0.25);
    padding: 12px 24px; border-radius: 10px; font-size: 0.9rem;
    font-family: 'Source Serif 4', serif; cursor: pointer;
    transition: background .2s;
}
.timer-btn-secondary:hover { background: rgba(255,255,255,0.18); }

/* Session log item */
.session-item {
    display: flex; align-items: center; gap: 16px;
    padding: 12px 0; border-bottom: 1px solid #F0F0F0;
}
.session-icon {
    width: 40px; height: 40px; border-radius: 50%;
    background: #DFF2DF;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem; flex-shrink: 0;
}
.session-info { flex: 1; }
.session-book { font-size: 0.9rem; font-weight: 600; color: #1F3F2E; margin-bottom: 2px; }
.session-date { font-size: 0.75rem; color: #8A8A8A; }
.session-dur {
    font-family: 'Playfair Display', serif;
    font-size: 1.05rem; font-weight: 700; color: #1F3F2E;
}

/* Health-style insight card */
.insight-health {
    background: white; border-radius: 14px; border: 1px solid #EBEBEB;
    padding: 18px 20px; margin-bottom: 12px; transition: border-color .2s;
}
.insight-health:hover { border-color: #3E7255; }
.insight-health .label {
    font-size: 0.72rem; text-transform: uppercase; letter-spacing: .1em;
    color: #8A8A8A; margin-bottom: 6px;
}
.insight-health .value {
    font-family: 'Playfair Display', serif;
    font-size: 1.8rem; font-weight: 700; color: #1F3F2E; line-height: 1;
}
.insight-health .unit { font-size: 0.8rem; color: #8A8A8A; margin-left: 4px; }
.insight-health .trend { font-size: 0.78rem; color: #3E7255; margin-top: 4px; }
.insight-health .trend.down { color: #D85A30; }

/* Period tab */
.period-tabs { display: flex; gap: 6px; margin-bottom: 20px; }
.period-tab {
    padding: 6px 18px; border-radius: 20px; font-size: 0.82rem;
    cursor: pointer; border: 1.5px solid #1F3F2E; background: white;
    color: #1F3F2E; font-family: 'Source Serif 4', serif; transition: all .2s;
    white-space: nowrap;
}
.period-tab.active { background: #1F3F2E; color: white; }

/* Mini bar chart bars */
.bar-chart { display: flex; align-items: flex-end; gap: 4px; height: 80px; }
.bar-item { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 3px; }
.bar { border-radius: 4px 4px 0 0; width: 100%; background: #DFF2DF;
       transition: background .2s; cursor: pointer; }
.bar:hover { background: #3E7255; }
.bar.today { background: #1F3F2E; }
.bar-lbl { font-size: 0.6rem; color: #8A8A8A; text-align: center; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# SESSION STATE — Timer logic
# =============================================================================
if "timer_running" not in st.session_state:
    st.session_state["timer_running"] = False
if "timer_start" not in st.session_state:
    st.session_state["timer_start"] = None
if "timer_elapsed" not in st.session_state:
    st.session_state["timer_elapsed"] = 0        # seconds accumulated before pause
if "current_book" not in st.session_state:
    st.session_state["current_book"] = ""
# Session log (stored in session only — cleared on browser refresh)
if "sessions_log" not in st.session_state:
    st.session_state["sessions_log"] = []


def format_time(seconds: int) -> str:
    """Format seconds as HH:MM:SS."""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


# Compute current elapsed time
def get_elapsed() -> int:
    base = st.session_state["timer_elapsed"]
    if st.session_state["timer_running"] and st.session_state["timer_start"]:
        base += int(time.time() - st.session_state["timer_start"])
    return base


spacer(24)

# =============================================================================
# LAYOUT: Timer (left) + Insights sidebar (right)
# =============================================================================
timer_col, insight_col = st.columns([2.2, 1.3])

# ── LEFT: Timer + Session log ─────────────────────────────────────────────
with timer_col:

    section_title("Reading Timer")
    st.markdown(
        '<p class="lt-muted">Track the time you spend reading. '
        'Every session counts toward your goals.</p>',
        unsafe_allow_html=True,
    )
    spacer(12)

    # ── Book selector (current session)
    # In production: pre-fills from GET /api/borrowings?status=active
    book_name = st.text_input(
        "What are you reading right now?",
        placeholder="e.g.  Dune — Frank Herbert",
        value=st.session_state["current_book"],
        key="book_input",
    )
    st.session_state["current_book"] = book_name

    spacer(16)

    # ── Timer display
    elapsed = get_elapsed()
    display_time = format_time(elapsed)
    book_label = st.session_state["current_book"] or "No book selected"
    status_sub  = "Reading in progress..." if st.session_state["timer_running"] else "Timer paused"

    st.markdown(f"""
    <div class="timer-card">
        <div class="timer-display">{display_time}</div>
        <div class="timer-sub">{status_sub}</div>
        <div class="timer-book-name">"{book_label}"</div>
    </div>
    """, unsafe_allow_html=True)

    spacer(16)

    # ── Timer controls
    btn_col1, btn_col2, btn_col3 = st.columns(3)

    with btn_col1:
        # START / PAUSE
        if not st.session_state["timer_running"]:
            if st.button(
                "▶ Start reading",
                type="primary",
                use_container_width=True,
                key="start_btn",
            ):
                if not st.session_state["current_book"]:
                    st.warning("Please enter the book you're reading first.")
                else:
                    st.session_state["timer_running"] = True
                    st.session_state["timer_start"] = time.time()
                    st.rerun()
        else:
            if st.button(
                "⏸ Pause",
                use_container_width=True,
                key="pause_btn",
            ):
                # Accumulate elapsed before pausing
                st.session_state["timer_elapsed"] = get_elapsed()
                st.session_state["timer_running"] = False
                st.session_state["timer_start"] = None
                st.rerun()

    with btn_col2:
        # SAVE SESSION
        # In production: POST /api/reading-sessions { book, duration_min, date }
        if st.button(
            "💾 Save session",
            use_container_width=True,
            key="save_btn",
        ):
            final_elapsed = get_elapsed()
            if final_elapsed < 10:
                st.warning("Read for at least a few seconds before saving!")
            else:
                mins = max(1, final_elapsed // 60)
                book = st.session_state["current_book"] or "Unknown book"
                now  = datetime.datetime.now().strftime("%b %d, %Y · %H:%M")
                st.session_state["sessions_log"].insert(0, {
                    "book": book,
                    "date": now,
                    "duration_min": mins,
                    "duration_display": format_time(final_elapsed),
                })
                # Reset timer after saving
                st.session_state["timer_running"]  = False
                st.session_state["timer_start"]    = None
                st.session_state["timer_elapsed"]  = 0
                st.session_state["current_book"]   = ""
                st.success(f"Session saved! {mins} min of reading logged.")
                st.rerun()

    with btn_col3:
        # RESET
        if st.button("↺ Reset", use_container_width=True, key="reset_btn"):
            st.session_state["timer_running"] = False
            st.session_state["timer_start"]   = None
            st.session_state["timer_elapsed"] = 0
            st.rerun()

    # Auto-refresh while timer is running (every 1 second)
    if st.session_state["timer_running"]:
        time.sleep(1)
        st.rerun()

    spacer(28)
    st.markdown('<hr style="border-color:#EBEBEB;">', unsafe_allow_html=True)

    # ── SESSION LOG ──────────────────────────────────────────────────────
    section_title("Session log")
    section_label("Your reading sessions this session")

    # Combine in-session logs with illustrative past sessions
    DEMO_SESSIONS = [
        {"book": "Dune",              "date": "May 21, 2026 · 21:30", "duration_min": 47, "duration_display": "00:47:12"},
        {"book": "Foundation",        "date": "May 20, 2026 · 19:15", "duration_min": 32, "duration_display": "00:32:05"},
        {"book": "The Name of the Wind", "date": "May 19, 2026 · 20:00", "duration_min": 55, "duration_display": "00:55:43"},
        {"book": "Sapiens",           "date": "May 18, 2026 · 09:30", "duration_min": 28, "duration_display": "00:28:17"},
        {"book": "1984",              "date": "May 17, 2026 · 22:00", "duration_min": 41, "duration_display": "00:41:08"},
    ]

    all_sessions = st.session_state["sessions_log"] + DEMO_SESSIONS

    if all_sessions:
        for s in all_sessions[:8]:
            st.markdown(f"""
            <div class="session-item">
                <div class="session-icon">📖</div>
                <div class="session-info">
                    <div class="session-book">{s['book']}</div>
                    <div class="session-date">{s['date']}</div>
                </div>
                <div class="session-dur">{s['duration_display']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown(
            '<p class="lt-muted">No sessions yet. Start the timer to begin tracking!</p>',
            unsafe_allow_html=True,
        )


# ── RIGHT: Trends & Insights sidebar ────────────────────────────────────
with insight_col:
    spacer(4)
    section_title("Reading trends")

    # Period selector
    # In production: selected period sent to GET /api/stats/reading-time?view=...
    period_options = ["Day", "Week", "Month", "6 months"]
    if "trend_period" not in st.session_state:
        st.session_state["trend_period"] = "Week"

    selected_period = st.radio(
        "View period",
        period_options,
        horizontal=True,
        index=period_options.index(st.session_state["trend_period"]),
        label_visibility="collapsed",
        key="period_radio",
    )
    st.session_state["trend_period"] = selected_period

    spacer(8)

    # ── INSIGHT CARDS (Apple Health style) ───────────────────────────────
    # In production: data from GET /api/stats/reading-time?user_id=<id>
    period_insights = {
        "Day": {
            "total": "1h 28",  "unit": "min today",   "trend": "+18 min vs yesterday", "up": True,
            "avg": "53",       "avg_unit": "min/day",  "sessions": "2",
            "longest": "47",   "longest_unit": "min",
        },
        "Week": {
            "total": "7h 14", "unit": "min this week",  "trend": "+2h 30 vs last week",  "up": True,
            "avg": "62",      "avg_unit": "min/day",    "sessions": "7",
            "longest": "55",  "longest_unit": "min",
        },
        "Month": {
            "total": "28h 40", "unit": "this month",  "trend": "+6h vs last month", "up": True,
            "avg": "58",       "avg_unit": "min/day",  "sessions": "24",
            "longest": "88",   "longest_unit": "min",
        },
        "6 months": {
            "total": "142h", "unit": "past 6 months",  "trend": "+38h vs prev. period", "up": True,
            "avg": "47",     "avg_unit": "min/day",    "sessions": "118",
            "longest": "104", "longest_unit": "min",
        },
    }

    ins = period_insights[selected_period]

    st.markdown(f"""
    <div class="insight-health">
        <div class="label">Total reading time</div>
        <div class="value">{ins['total']}
            <span class="unit">{ins['unit']}</span>
        </div>
        <div class="trend {'down' if not ins['up'] else ''}">
            {'↑' if ins['up'] else '↓'} {ins['trend']}
        </div>
    </div>
    <div class="insight-health">
        <div class="label">Daily average</div>
        <div class="value">{ins['avg']}
            <span class="unit">{ins['avg_unit']}</span>
        </div>
    </div>
    <div class="insight-health">
        <div class="label">Sessions logged</div>
        <div class="value">{ins['sessions']}
            <span class="unit">sessions</span>
        </div>
    </div>
    <div class="insight-health">
        <div class="label">Longest session</div>
        <div class="value">{ins['longest']}
            <span class="unit">{ins['longest_unit']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    spacer(16)
    st.markdown('<hr style="border-color:#EBEBEB;">', unsafe_allow_html=True)

    # ── MINI BAR CHART ────────────────────────────────────────────────────
    section_label("Reading time per day")

    # In production: data from GET /api/stats/reading-time?view=week
    chart_data = {
        "Day":       [{"l": "00h", "v": 0}, {"l": "04h", "v": 0}, {"l": "08h", "v": 12},
                      {"l": "12h", "v": 8}, {"l": "16h", "v": 32}, {"l": "20h", "v": 47}, {"l": "now", "v": 1, "today": True}],
        "Week":      [{"l": "Mon", "v": 28}, {"l": "Tue", "v": 45}, {"l": "Wed", "v": 32},
                      {"l": "Thu", "v": 55}, {"l": "Fri", "v": 41}, {"l": "Sat", "v": 60},
                      {"l": "Sun", "v": 47, "today": True}],
        "Month":     [{"l": "W1", "v": 210}, {"l": "W2", "v": 280}, {"l": "W3", "v": 245}, {"l": "W4", "v": 275, "today": True}],
        "6 months":  [{"l": "Dec", "v": 940}, {"l": "Jan", "v": 1100}, {"l": "Feb", "v": 890},
                      {"l": "Mar", "v": 1240}, {"l": "Apr", "v": 1050}, {"l": "May", "v": 1120, "today": True}],
    }

    bars = chart_data[selected_period]
    max_v = max(b["v"] for b in bars) or 1

    bars_html = '<div class="bar-chart">'
    for bar in bars:
        pct = int(bar["v"] / max_v * 100) if max_v > 0 else 0
        today_cls = " today" if bar.get("today") else ""
        bars_html += f"""
        <div class="bar-item">
            <div class="bar{today_cls}" style="height:{max(pct, 3)}%;"></div>
            <div class="bar-lbl">{bar['l']}</div>
        </div>"""
    bars_html += "</div>"

    st.markdown(bars_html, unsafe_allow_html=True)

    spacer(16)
    st.markdown('<hr style="border-color:#EBEBEB;">', unsafe_allow_html=True)

    # ── GOAL PROGRESS ─────────────────────────────────────────────────────
    section_label("Daily reading goal")

    # In production: goal from user settings, progress from API
    goal_min = 60     # minutes per day (configurable in settings)
    done_min = 88     # minutes read today (from API)
    goal_pct = min(int(done_min / goal_min * 100), 100)

    st.markdown(
        f'<div style="display:flex;justify-content:space-between;'
        f'font-size:.82rem;margin-bottom:4px;">'
        f'<span style="color:#1F3F2E;font-weight:600;">{done_min} min read</span>'
        f'<span class="lt-muted">Goal: {goal_min} min</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Progress bar (green if goal met, gold if over)
    bar_color = COLORS["gold"] if goal_pct >= 100 else COLORS["dark_green"]
    st.markdown(
        f'<div style="background:#E8E8E8;border-radius:8px;height:10px;">'
        f'<div style="background:{bar_color};border-radius:8px;'
        f'height:10px;width:{goal_pct}%;transition:width .4s;"></div>'
        f'</div>'
        f'<p style="font-size:.75rem;color:#3E7255;margin-top:6px;">'
        f'{"✓ Daily goal reached! Great work." if goal_pct >= 100 else f"{goal_min - done_min} min remaining today"}'
        f'</p>',
        unsafe_allow_html=True,
    )

    spacer(12)

    # Change daily goal
    # In production: PUT /api/users/<id>/settings { reading_goal_min: <value> }
    new_goal = st.number_input(
        "Change daily goal (min)",
        min_value=10,
        max_value=300,
        value=goal_min,
        step=5,
        key="goal_input",
    )
    if st.button("Save goal", use_container_width=True, key="save_goal"):
        st.toast(f"Daily reading goal set to {new_goal} min!")

page_spacer(20)
#--------------------------------------------------------------------NAVIGATION
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
section_title("Navigation")
render_navigation_section()