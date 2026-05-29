import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Backend.Functions.library_data import (
    get_genres,
    get_reader_from_session,
    get_reader_genres,
    update_reader_profile,
)
from components.ui_helpers import (
    inject_global_css,
    page_spacer,
    render_login_required,
    render_navbar,
    section_title, render_navigation_section,
)


st.set_page_config(
    page_title="Settings | LibTrack",
    page_icon="LT",
    layout="wide",
    initial_sidebar_state="collapsed"
)

inject_global_css()
render_navbar(active_page="my_library")
page_spacer(24)


current_reader = get_reader_from_session(st.session_state)
if current_reader is None:
    render_login_required("Please sign in to manage reader settings.")
    st.stop()


_, center_col, _ = st.columns([0.5, 3, 0.5])

with center_col:
    st.markdown("<h1>Reader Settings</h1>", unsafe_allow_html=True)
    st.markdown(
        '<p class="muted">Manage fields stored in the readers table.</p>',
        unsafe_allow_html=True,
    )

    page_spacer(10)
    st.markdown("<hr>", unsafe_allow_html=True)

    section_title("Reader information")

    new_name = st.text_input(
        "Name",
        value=current_reader["Name"] or "",
        key="settings_reader_name",
        help="Saved to readers.Name.",
    )

    st.text_input(
        "Email",
        value=current_reader["Email"] or "",
        key="settings_reader_email",
        disabled=True,
        help="Saved in readers.Email. Email editing is not enabled on this page.",
    )

    genre_list = get_genres(include_all=False)
    saved_genres = [genre for genre in get_reader_genres(current_reader) if genre in genre_list]

    new_genres = st.multiselect(
        "Preferred genres",
        options=genre_list,
        default=saved_genres,
        key="settings_genres",
        help="Saved as a comma-separated value in readers.Preferred_Category.",
    )

    page_spacer(8)
    st.markdown("<hr>", unsafe_allow_html=True)

    section_title("Reader preferences")

    # webb: Keep one recommendation switch; off means the reader is not included in recommendations.
    receive_recs = st.toggle(
        "Enable personalized book recommendations",
        value=bool(current_reader.get("Receive_Recommendations")),
        key="settings_recs",
        help=(
            "Saved to readers.Receive_Recommendations. "
            "When off, LibTrack hides personalized recommendation cards and stops generating recommendation rows."
        ),
    )
    st.caption(
        "When this is off, LibTrack hides personalized recommendation cards, "
        "does not generate rows in the recommendations table for you, and still shows Popular Books."
    )

    if not receive_recs:
        st.info(
            "Personalized recommendations are disabled. "
            "Hidden content: Recommend to You cards and generated recommendation rows. "
            "Still visible: Popular Books and community discovery."
        )

    page_spacer(16)

    save_col, cancel_col = st.columns([3, 1])
    with save_col:
        if st.button("Save changes", type="primary", use_container_width=True, key="save_settings"):
            if not new_name.strip():
                st.error("Name is required.")
            else:
                success, message = update_reader_profile(
                    reader_id=current_reader["Reader_ID"],
                    name=new_name.strip(),
                    preferred_category=", ".join(new_genres),
                    receive_recommendations=receive_recs,
                    show_reading_history=bool(current_reader.get("Show_Reading_History")),
                )
                if success:
                    st.session_state["reader_name"] = new_name.strip()
                    st.session_state["preferred_category"] = ", ".join(new_genres)
                    st.success("Reader settings saved successfully.")
                else:
                    st.error(message)

    with cancel_col:
        if st.button("Cancel", use_container_width=True, key="cancel_settings"):
            st.switch_page("pages/08_Profile.py")

page_spacer(20)
#--------------------------------------------------------------------NAVIGATION
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
section_title("Navigation")
render_navigation_section()
