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
from components.ui_helpers import inject_global_css, page_spacer, render_navbar, section_title


st.set_page_config(
    page_title="Settings | LibTrack",
    page_icon="LT",
    layout="wide",
)

inject_global_css()
render_navbar(active_page="my_library")
page_spacer(24)


current_reader = get_reader_from_session(st.session_state)
if current_reader is None:
    st.warning("Please sign in to manage reader settings.")
    if st.button("Go to Login", type="primary"):
        st.switch_page("pages/01_Login.py")
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

    receive_recs = st.toggle(
        "Enable personalized book recommendations",
        value=bool(current_reader.get("Receive_Recommendations")),
        key="settings_recs",
        help="Saved to readers.Receive_Recommendations.",
    )

    show_history = st.toggle(
        "Show my reading history",
        value=bool(current_reader.get("Show_Reading_History")),
        key="settings_history",
        help="Saved to readers.Show_Reading_History.",
    )

    if not receive_recs:
        st.info("Personalized recommendations are disabled. You will still see popular books.")

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
                    show_reading_history=show_history,
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
