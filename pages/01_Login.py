import os
import sys

import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.ui_helpers import inject_global_css, page_spacer, render_navbar
from UI.Login.auth import login_reader
from UI.Login.session import google_user_is_logged_in, set_reader_session, sync_google_user_to_session


st.set_page_config(
    page_title="Login | LibTrack",
    page_icon="LT",
    layout="wide",
)

inject_global_css()
render_navbar()
page_spacer(50)

if google_user_is_logged_in(st.user) and not st.session_state.get("logged_in", False):
    google_success, google_message, google_reader = sync_google_user_to_session(
        st.session_state,
        st.user,
    )

    if google_success and google_reader:
        st.success(f"Welcome back, {google_reader['Name']}!")
        st.switch_page("app.py")
    else:
        st.error(google_message)
        if st.button("Sign out of Google", type="primary"):
            st.logout()
        st.stop()


_, center_col, _ = st.columns([1, 1.4, 1])

with center_col:
    st.markdown(
        '<div style="text-align:center; margin-bottom:32px;">'
        '<span style="font-size:2.5rem;">LT</span><br>'
        '<h1 style="font-size:1.8rem; margin-top:8px;">Welcome back</h1>'
        '<p class="muted">Sign in to continue your reading journey</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    email_input = st.text_input(
        "Email",
        placeholder="reader@gmail.com",
        key="login_email",
    )

    password_input = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password",
        key="login_password",
    )

    page_spacer(4)

    st.markdown(
        '<div style="text-align:right; margin-bottom:16px;">'
        '<span class="muted" style="cursor:pointer; font-size:0.85rem;">'
        'Forgot password?</span></div>',
        unsafe_allow_html=True,
    )

    login_btn = st.button(
        "Sign in",
        type="primary",
        use_container_width=True,
        key="login_btn",
    )

    if login_btn:
        if not email_input or not password_input:
            st.error("Please fill in all fields.")
        else:
            result = login_reader(email_input, password_input)

            if len(result) == 3:
                success, message, reader = result
            else:
                success, message = result
                reader = None

            if success and reader:
                set_reader_session(st.session_state, reader)

                st.success(f"Welcome back, {reader['Name']}!")
                st.switch_page("app.py")
            else:
                st.error(message)

    page_spacer(12)
    st.markdown("<hr>", unsafe_allow_html=True)
    page_spacer(4)

    if st.button("Continue with Google", use_container_width=True, key="google_login_btn"):
        try:
            st.login("google")
        except Exception:
            st.error("Google login is not configured yet.")
            st.caption(
                "Add .streamlit/secrets.toml with Google OAuth credentials, "
                "then restart Streamlit."
            )

    page_spacer(16)
    st.markdown("<hr>", unsafe_allow_html=True)
    page_spacer(8)

    st.markdown(
        '<div style="text-align:center;" class="muted">Do not have an account yet?</div>',
        unsafe_allow_html=True,
    )

    if st.button("Create an account", use_container_width=True, key="go_register"):
        st.switch_page("pages/02_Register.py")
