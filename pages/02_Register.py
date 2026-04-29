# =============================================================================
# FILE: pages/02_Register.py
# PURPOSE: Registration page for new LibTrack users.
#
# FUTURE BACK-END INTEGRATION:
#   - On submit: POST /api/auth/register with user data
#   - Preferred genres stored in the `user_preferences` table
#   - Recommendation toggle stored in user profile settings
#   - On success: redirect to Login page or auto-login
# =============================================================================

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.ui_helpers import inject_global_css, render_navbar, page_spacer, COLORS
from data.mock_data import GENRES

st.set_page_config(
    page_title="Register — LibTrack",
    page_icon="📖",
    layout="wide",
)
inject_global_css()
render_navbar()
page_spacer(40)

_, center_col, _ = st.columns([1, 1.6, 1])

with center_col:
    st.markdown(
        '<div style="text-align:center; margin-bottom:28px;">'
        '<span style="font-size:2.2rem;">📖</span><br>'
        '<h1 style="font-size:1.8rem; margin-top:8px;">Join LibTrack</h1>'
        '<p class="muted">Start your reading journey today</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    # -------------------------------------------------------------------------
    # USERNAME INPUT
    # In production: sent to POST /api/auth/register as `username`.
    # The API checks for uniqueness before creating the account.
    # -------------------------------------------------------------------------
    username_input = st.text_input(
        "Username",
        placeholder="marie_reads",
        key="reg_username",
    )

    # -------------------------------------------------------------------------
    # EMAIL INPUT
    # In production: sent as `email` to POST /api/auth/register.
    # Must be a valid and unique email address.
    # -------------------------------------------------------------------------
    email_input = st.text_input(
        "Email address",
        placeholder="marie@email.com",
        key="reg_email",
    )

    col_pw1, col_pw2 = st.columns(2)

    # -------------------------------------------------------------------------
    # PASSWORD + CONFIRM PASSWORD
    # In production: hashed client-side before sending to the API.
    # Server will also verify the hash during login.
    # -------------------------------------------------------------------------
    with col_pw1:
        password_input = st.text_input(
            "Password",
            type="password",
            placeholder="At least 8 characters",
            key="reg_pw",
        )
    with col_pw2:
        confirm_pw = st.text_input(
            "Confirm password",
            type="password",
            placeholder="Repeat your password",
            key="reg_pw_confirm",
        )

    page_spacer(8)

    # -------------------------------------------------------------------------
    # PREFERRED GENRES MULTI-SELECT
    # In production: stored in the `user_preferences` table as a list of
    # genre_id values. Used by the recommendation system.
    # -------------------------------------------------------------------------
    genre_list = [g for g in GENRES if g != "All genres"]
    preferred_genres = st.multiselect(
        "Preferred book genres (choose all that apply)",
        options=genre_list,
        default=["Science fiction", "Fiction"],
        key="reg_genres",
        help="Your selection helps us recommend books you'll love.",
    )

    page_spacer(4)

    # -------------------------------------------------------------------------
    # PERSONALIZED RECOMMENDATIONS TOGGLE
    # In production: stored as `receive_recommendations` (boolean) in the
    # user_settings table. Affects whether the recommendation engine
    # generates suggestions for this user.
    # -------------------------------------------------------------------------
    receive_recs = st.toggle(
        "Enable personalized book recommendations",
        value=True,
        key="reg_recs",
        help="You can change this at any time in Settings.",
    )

    page_spacer(8)

    # -------------------------------------------------------------------------
    # CREATE ACCOUNT BUTTON
    # In production: sends all form data to POST /api/auth/register
    # -------------------------------------------------------------------------
    register_btn = st.button(
        "Create my account",
        type="primary",
        use_container_width=True,
        key="reg_submit",
    )

    if register_btn:
        # MOCK VALIDATION — replace with real API call in production
        errors = []
        if not username_input:
            errors.append("Username is required.")
        if not email_input or "@" not in email_input:
            errors.append("A valid email address is required.")
        if len(password_input) < 8:
            errors.append("Password must be at least 8 characters.")
        if password_input != confirm_pw:
            errors.append("Passwords do not match.")
        if not preferred_genres:
            errors.append("Please select at least one genre.")

        if errors:
            for err in errors:
                st.error(err)
        else:
            st.success("Account created successfully! You can now log in.")
            # In production: auto-login or redirect to login page
            st.balloons()

    page_spacer(12)
    st.markdown('<hr>', unsafe_allow_html=True)
    page_spacer(4)

    st.markdown(
        '<div style="text-align:center;" class="muted">Already have an account?</div>',
        unsafe_allow_html=True,
    )
    if st.button("Sign in", use_container_width=True, key="go_login"):
        st.switch_page("pages/01_Login.py")