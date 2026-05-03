import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from Backend.Functions.library_data import get_genres
from components.ui_helpers import inject_global_css, page_spacer, render_navbar
from UI.Login.auth import register_reader


st.set_page_config(
    page_title="Register | LibTrack",
    page_icon="LT",
    layout="wide",
)

inject_global_css()
render_navbar()
page_spacer(40)


_, center_col, _ = st.columns([1, 1.6, 1])

with center_col:
    st.markdown(
        '<div style="text-align:center; margin-bottom:28px;">'
        '<span style="font-size:2.2rem;">LT</span><br>'
        '<h1 style="font-size:1.8rem; margin-top:8px;">Join LibTrack</h1>'
        '<p class="muted">Start your reading journey today</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    name_input = st.text_input(
        "Name",
        placeholder="Reader name",
        key="reg_name",
    )

    email_input = st.text_input(
        "Email address",
        placeholder="reader@email.com",
        key="reg_email",
    )

    col_pw1, col_pw2 = st.columns(2)

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

    genre_list = get_genres(include_all=False)
    default_genres = [genre for genre in ["Science fiction", "Fiction"] if genre in genre_list]

    preferred_genres = st.multiselect(
        "Preferred book genres",
        options=genre_list,
        default=default_genres,
        key="reg_genres",
        help="Your selection is stored in readers.Preferred_Category.",
    )

    page_spacer(4)

    receive_recs = st.toggle(
        "Enable personalized book recommendations",
        value=True,
        key="reg_recs",
        help="This is stored in readers.Receive_Recommendations.",
    )

    page_spacer(8)

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
            for error in errors:
                st.error(error)
        else:
            success, message = register_reader(
                name=name_input,
                email=email_input,
                password=password_input,
                preferred_category=", ".join(preferred_genres),
                receive_recommendations=receive_recs,
            )

            if success:
                st.success(message)
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
