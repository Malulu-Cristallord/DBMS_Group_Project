# =============================================================================
# FILE: pages/02_Register.py
# PURPOSE: Registration page for new LibTrack users.
#
# BACK-END INTEGRATION:
#   - On submit, the page calls register_user().
#   - Reader data is inserted into the readers table.
#   - Preferred genres are stored as a comma-separated string in Preferred_Category.
#   - Recommendation preference is stored in Receive_Recommendations.
#   - On success, the user is redirected to the Login page.
# =============================================================================

import streamlit as st
import sys
import os

# Allow this page to import modules from the project root directory.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.ui_helpers import inject_global_css, render_navbar, page_spacer
from data.mock_data import GENRES
from UI.Login.auth import register_user


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
    # NAME INPUT
    # This value is stored in readers.Name.
    # -------------------------------------------------------------------------
    name_input = st.text_input(
        "Name",
        placeholder="Marie",
        key="reg_name",
    )

    # -------------------------------------------------------------------------
    # EMAIL INPUT
    # This value is stored in readers.Email.
    # The database also checks that Email is unique.
    # -------------------------------------------------------------------------
    email_input = st.text_input(
        "Email address",
        placeholder="marie@email.com",
        key="reg_email",
    )

    col_pw1, col_pw2 = st.columns(2)

    # -------------------------------------------------------------------------
    # PASSWORD + CONFIRM PASSWORD
    # The plain-text password is sent to register_user(), then hashed with bcrypt
    # before being stored in readers.Password_Hash.
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
    # The selected genres are stored as a comma-separated string in
    # readers.Preferred_Category.
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
    # This value is stored in readers.Receive_Recommendations.
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
    # Calls the back-end register_user() function.
    # -------------------------------------------------------------------------
    register_btn = st.button(
        "Create my account",
        type="primary",
        use_container_width=True,
        key="reg_submit",
    )

    if register_btn:
        errors = []

        if not name_input:
            errors.append("Name is required.")

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
            preferred_category = ", ".join(preferred_genres)

            success, message = register_user(
                name=name_input,
                email=email_input,
                password=password_input,
                preferred_category=preferred_category,
                receive_recommendations=receive_recs,
            )

            if success:
                st.success(message)
                st.balloons()
                st.switch_page("pages/01_Login.py")
            else:
                st.error(message)

    page_spacer(12)
    st.markdown("<hr>", unsafe_allow_html=True)
    page_spacer(4)

    st.markdown(
        '<div style="text-align:center;" class="muted">Already have an account?</div>',
        unsafe_allow_html=True,
    )

    if st.button("Sign in", use_container_width=True, key="go_login"):
        st.switch_page("pages/01_Login.py")