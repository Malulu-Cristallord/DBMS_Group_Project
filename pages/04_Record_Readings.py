
import streamlit as st
import time
import datetime
import sys, os
from streamlit_autorefresh import st_autorefresh
from datetime import timedelta

from Backend.Functions.badges_handler import reader_add_books_read
from Backend.Functions.library_data import get_reader_from_session, get_books_by_title, get_books
from Backend.Functions.post_handler import get_book_by_isbn
from Backend.Functions.reader import save_reading_session_time

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
    initial_sidebar_state="collapsed"
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
if "reading_goal" not in st.session_state:
    st.session_state["reading_goal"] = 60
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



section_title("Reading Timer")
st.markdown(
    '<p class="lt-muted">Track the time you spend reading. '
    'Every session counts toward your goals.</p>',
    unsafe_allow_html=True,
)
spacer(12)

# ── Book selector (current session)
# In production: pre-fills from GET /api/borrowings?status=active
search_type = st.radio("Search by", ["Title", "ISBN"], horizontal=True)

if search_type == "Title":
    keyword = st.text_input("Enter book title")
    books = get_books_by_title(keyword) if keyword else []
else:
    isbn = st.text_input("Enter ISBN")
    books = get_book_by_isbn(isbn) if isbn else []

book_options = {"No book linked": None}
get_books()
book_options.update({f'{b["Title"]} - {b["Author"]}': b["ISBN"] for b in books})
linked_book = st.selectbox("Select book", list(book_options.keys()))
st.session_state["current_book"] = linked_book
st.write("Selected book:", linked_book)

spacer(16)

# ── Timer display
elapsed = get_elapsed()
display_time = format_time(elapsed)
book_label = linked_book if linked_book else "No book selected"
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
            if not linked_book:
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
            if final_elapsed > 120:
                reader_add_books_read(current_reader["Reader_ID"])
                st.success("Congrats on finishing a reading session! Check the badges page to see if you've earned any new badges.")
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
            save_reading_session_time(current_reader["Reader_ID"], final_elapsed)
            st.success(f"Session saved! {mins} min of reading logged.")
            st.rerun()

with btn_col3:
    # RESET
    if st.button("↺ Reset", use_container_width=True, key="reset_btn"):
        st.session_state["timer_running"] = False
        st.session_state["timer_start"]   = None
        st.session_state["timer_elapsed"] = 0
        st.rerun()

# Auto-refresh while timer is running (every 5 seconds)
if st.session_state["timer_running"]:
    st_autorefresh(interval=1000, key="timer_refresh")

spacer(28)
st.markdown('<hr style="border-color:#EBEBEB;">', unsafe_allow_html=True)

#--------------------------------------------------------------------NAVIGATION
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
section_title("Navigation")
render_navigation_section()