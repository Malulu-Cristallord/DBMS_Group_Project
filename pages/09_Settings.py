# =============================================================================
# FILE: pages/09_Settings.py
# PURPOSE: User settings page — edit profile and manage preferences.
#
# FUTURE BACK-END INTEGRATION:
#   - Save changes: PUT /api/users/<user_id>/profile
#   - Privacy settings: PUT /api/users/<user_id>/privacy
#   - All toggles update the user_settings table in the database.
#   - The recommendation toggle enables/disables the recommendation engine
#     for this specific user.
# =============================================================================

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.ui_helpers import (
    inject_global_css, render_navbar,
    page_spacer, section_title, COLORS,
)
from data.mock_data import CURRENT_USER, GENRES

st.set_page_config(
    page_title="Settings — LibTrack",
    page_icon="📖",
    layout="wide",
)
inject_global_css()
render_navbar(active_page="my_library")
page_spacer(24)

_, center_col, _ = st.columns([0.5, 3, 0.5])

with center_col:
    st.markdown('<h1>Account Settings</h1>', unsafe_allow_html=True)
    st.markdown('<p class="muted">Manage your profile, privacy, and preferences.</p>', unsafe_allow_html=True)

    page_spacer(10)
    st.markdown('<hr>', unsafe_allow_html=True)

    # =========================================================================
    # SECTION 1: PROFILE INFORMATION
    # In production: PUT /api/users/<user_id>/profile
    # =========================================================================
    section_title("Profile information")

    # -------------------------------------------------------------------------
    # USERNAME EDIT
    # In production: sent as `username` to PUT /api/users/<id>/profile
    # Must be unique — the API will check for conflicts.
    # -------------------------------------------------------------------------
    new_username = st.text_input(
        "Username",
        value=CURRENT_USER["username"],
        key="settings_username",
    )

    # -------------------------------------------------------------------------
    # BIO EDIT
    # In production: stored as `bio` text in the users table.
    # -------------------------------------------------------------------------
    new_bio = st.text_area(
        "Bio",
        value=CURRENT_USER["bio"],
        height=100,
        key="settings_bio",
    )

    # -------------------------------------------------------------------------
    # PREFERRED GENRES
    # In production: updates the user_preferences table.
    # Used by the recommendation engine to filter book suggestions.
    # -------------------------------------------------------------------------
    genre_list = [g for g in GENRES if g != "All genres"]
    new_genres = st.multiselect(
        "Preferred genres",
        options=genre_list,
        default=CURRENT_USER["preferred_genres"],
        key="settings_genres",
    )

    page_spacer(8)
    st.markdown('<hr>', unsafe_allow_html=True)

    # =========================================================================
    # SECTION 2: PRIVACY SETTINGS
    # In production: PUT /api/users/<user_id>/privacy
    # Stored in the user_privacy_settings table.
    # =========================================================================
    section_title("Privacy")

    col1, col2 = st.columns(2)
    with col1:
        # In production: `is_public` field in users table
        public_profile = st.toggle(
            "Public profile",
            value=CURRENT_USER["public_profile"],
            key="settings_public",
            help="When off, only followers can see your profile.",
        )

        # In production: `show_reviews` field in user_privacy_settings
        show_reviews = st.toggle(
            "Show my reviews publicly",
            value=True,
            key="settings_show_reviews",
        )

    with col2:
        # In production: `allow_followers` field in user_privacy_settings
        allow_followers = st.toggle(
            "Allow others to follow me",
            value=CURRENT_USER["allow_followers"],
            key="settings_follow",
        )

        # In production: `show_borrowings` field in user_privacy_settings
        show_borrowings = st.toggle(
            "Make my borrowings public",
            value=CURRENT_USER["show_borrowings"],
            key="settings_borrowings",
        )

    page_spacer(8)
    st.markdown('<hr>', unsafe_allow_html=True)

    # =========================================================================
    # SECTION 3: RECOMMENDATIONS
    # In production: `receive_recommendations` boolean in user_settings.
    # When False, the recommendation engine skips this user entirely.
    # =========================================================================
    section_title("Recommendations")

    # -------------------------------------------------------------------------
    # RECOMMENDATION TOGGLE
    # In production: PUT /api/users/<id>/settings { receive_recommendations: bool }
    # This setting controls whether the recommendation system generates
    # personalized book suggestions for this user.
    # -------------------------------------------------------------------------
    receive_recs = st.toggle(
        "Enable personalized book recommendations",
        value=CURRENT_USER["receive_recommendations"],
        key="settings_recs",
        help=(
            "When enabled, we use your reading history, ratings, and preferred genres "
            "to suggest books you might enjoy."
        ),
    )

    if not receive_recs:
        st.info("Personalized recommendations are disabled. You will still see popular books.")

    page_spacer(16)

    # =========================================================================
    # SAVE BUTTON
    # In production: triggers PUT /api/users/<id>/profile and
    # PUT /api/users/<id>/privacy with all form values.
    # =========================================================================
    save_col, cancel_col = st.columns([3, 1])
    with save_col:
        if st.button("Save changes", type="primary", use_container_width=True, key="save_settings"):
            # MOCK: In production, all changed values are sent to the API
            st.success("Settings saved successfully!")

    with cancel_col:
        if st.button("Cancel", use_container_width=True, key="cancel_settings"):
            st.switch_page("pages/08_Profile.py")