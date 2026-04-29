# =============================================================================
# FILE: pages/01_Login.py
# PURPOSE: Login page for LibTrack.
#          Users enter their email/username and password to access the platform.
#
# FUTURE BACK-END INTEGRATION:
#   - The login form will send a POST request to /api/auth/login
#   - The API will return a JWT token stored in session/cookies
#   - On success: redirect to Home Feed
#   - On failure: show an error message from the API response
# =============================================================================

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.ui_helpers import inject_global_css, render_navbar, page_spacer, COLORS
from data.mock_data import CURRENT_USER

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="Login — LibTrack",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed",
)
inject_global_css()
render_navbar()
page_spacer(50)

# =============================================================================
# LOGIN FORM
# =============================================================================
# Center the form using columns
_, center_col, _ = st.columns([1, 1.4, 1])

with center_col:
    # Logo and title
    st.markdown(
        f'<div style="text-align:center; margin-bottom:32px;">'
        f'<span style="font-size:2.5rem;">📖</span><br>'
        f'<h1 style="font-size:1.8rem; margin-top:8px;">Welcome back</h1>'
        f'<p class="muted">Sign in to continue your reading journey</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # -------------------------------------------------------------------------
    # USERNAME / EMAIL INPUT
    # In production: this value is sent as the `identifier` field to
    # POST /api/auth/login — can be either email or username.
    # -------------------------------------------------------------------------
    email_input = st.text_input(
        "Email or username",
        placeholder="marie@email.com",
        key="login_email",
    )

    # -------------------------------------------------------------------------
    # PASSWORD INPUT
    # In production: this value is sent as the `password` field to
    # POST /api/auth/login (it will be hashed before sending).
    # -------------------------------------------------------------------------
    password_input = st.text_input(
        "Password",
        type="password",
        placeholder="••••••••",
        key="login_password",
    )

    page_spacer(4)

    # Forgot password link
    # In production: clicking this triggers POST /api/auth/forgot-password
    st.markdown(
        f'<div style="text-align:right; margin-bottom:16px;">'
        f'<span class="muted" style="cursor:pointer; font-size:0.85rem;">'
        f'Forgot password?</span></div>',
        unsafe_allow_html=True,
    )

    # -------------------------------------------------------------------------
    # LOGIN BUTTON
    # In production: clicking this sends the login request to the API.
    # Currently performs mock validation only.
    # -------------------------------------------------------------------------
    login_btn = st.button("Sign in", type="primary", use_container_width=True, key="login_btn")

    if login_btn:
        # MOCK VALIDATION — replace with real API call in production
        # Real call: response = requests.post("/api/auth/login", json={...})
        if email_input == "" or password_input == "":
            st.error("Please fill in all fields.")
        elif email_input in [CURRENT_USER["email"], CURRENT_USER["username"]] and password_input == "password":
            # In production: store the JWT token in st.session_state
            st.session_state["logged_in"] = True
            st.session_state["user"] = CURRENT_USER
            st.success(f"Welcome back, {CURRENT_USER['username']}! Redirecting...")
            st.switch_page("original_app.py")
        else:
            st.error("Incorrect email or password. (Hint: use 'marie@email.com' and 'password')")

    page_spacer(16)
    st.markdown('<hr>', unsafe_allow_html=True)
    page_spacer(8)

    # Link to register page
    st.markdown(
        '<div style="text-align:center;" class="muted">Don\'t have an account yet?</div>',
        unsafe_allow_html=True,
    )

    # In production: this navigates to the registration route
    if st.button("Create an account", use_container_width=True, key="go_register"):
        st.switch_page("pages/02_Register.py")