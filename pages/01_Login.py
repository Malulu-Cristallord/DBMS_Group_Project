# =============================================================================
# FILE: pages/01_Login.py
# PURPOSE: Login page for LibTrack.
#          Users enter their email and password to access the platform.
#
# BACK-END INTEGRATION:
#   - The login form calls login_user() from the authentication module.
#   - login_user() checks the readers table in MySQL.
#   - On success, reader information is stored in st.session_state.
#   - On failure, an error message is displayed.
# =============================================================================

import streamlit as st
import sys
import os

# Allow this page to import modules from the project root directory.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from components.ui_helpers import inject_global_css, render_navbar, page_spacer
from UI.Login.auth import login_user


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="Login — LibTrack",
    page_icon="📖",
    layout="wide",
)

inject_global_css()
render_navbar()
page_spacer(50)


# =============================================================================
# LOGIN FORM
# =============================================================================
_, center_col, _ = st.columns([1, 1.4, 1])

with center_col:
    # Logo and title
    st.markdown(
        '<div style="text-align:center; margin-bottom:32px;">'
        '<span style="font-size:2.5rem;">📖</span><br>'
        '<h1 style="font-size:1.8rem; margin-top:8px;">Welcome back</h1>'
        '<p class="muted">Sign in to continue your reading journey</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    # -------------------------------------------------------------------------
    # EMAIL INPUT
    # This value is used to find the reader account in the readers table.
    # -------------------------------------------------------------------------
    email_input = st.text_input(
        "Email",
        placeholder="marie@email.com",
        key="login_email",
    )

    # -------------------------------------------------------------------------
    # PASSWORD INPUT
    # The plain-text password is verified against the hashed password stored
    # in the readers table.
    # -------------------------------------------------------------------------
    password_input = st.text_input(
        "Password",
        type="password",
        placeholder="••••••••",
        key="login_password",
    )

    page_spacer(4)

    # Forgot password link
    # This is currently only a UI placeholder.
    st.markdown(
        '<div style="text-align:right; margin-bottom:16px;">'
        '<span class="muted" style="cursor:pointer; font-size:0.85rem;">'
        'Forgot password?</span></div>',
        unsafe_allow_html=True,
    )

    # -------------------------------------------------------------------------
    # LOGIN BUTTON
    # Calls the back-end login_user() function.
    # -------------------------------------------------------------------------
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
            result = login_user(email_input, password_input)
            # return three things: whether it succeeded or not, a success message, 
            # and the user's information (Dictionary form, as shown below).

            # Expected result format:
            # success, message, user = login_user(email, password)
            #
            # user should be a dictionary like:
            # {
            #     "Reader_ID": 1,
            #     "Name": "Webb",
            #     "Email": "webb@email.com",
            #     "Password_Hash": "...",
            #     "Preferred_Category": "...",
            #     "Points": 0
            # }

            if len(result) == 3:
                success, message, user = result
            else:
                success, message = result
                user = None

            if success and user:
                st.session_state["logged_in"] = True
                st.session_state["reader_id"] = user["Reader_ID"]
                st.session_state["reader_name"] = user["Name"]
                st.session_state["reader_email"] = user["Email"]
                st.session_state["preferred_category"] = user.get("Preferred_Category")
                st.session_state["points"] = user.get("Points", 0)

                st.success(f"Welcome back, {user['Name']}!")
                st.switch_page("app.py")
            else:
                st.error(message)

    page_spacer(16)
    st.markdown("<hr>", unsafe_allow_html=True)
    page_spacer(8)

    # Link to register page
    st.markdown(
        '<div style="text-align:center;" class="muted">Don\'t have an account yet?</div>',
        unsafe_allow_html=True,
    )

    if st.button("Create an account", use_container_width=True, key="go_register"):
        st.switch_page("pages/02_Register.py")