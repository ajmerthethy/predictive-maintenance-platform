import requests
import streamlit as st

from lib.api_client import API_URL


def require_login():
    """Call at the top of every page, right after st.set_page_config().

    Single-customer pilot auth: shows a login form and halts page
    execution (st.stop()) until a valid token is in session_state.
    """

    if st.session_state.get("auth_token"):
        return

    st.title("🏭 Predictive Maintenance Platform")
    st.subheader("Sign in")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign in")

    if submitted:
        try:
            response = requests.post(
                f"{API_URL}/auth/login",
                json={"username": username, "password": password},
                timeout=10,
            )
        except requests.exceptions.RequestException:
            st.error("Could not reach the server. Please try again.")
            st.stop()

        if response.status_code == 200:
            st.session_state.auth_token = response.json()["access_token"]
            st.rerun()
        else:
            st.error("Invalid username or password.")

    st.stop()


def logout_button():
    if st.sidebar.button("Log out"):
        st.session_state.pop("auth_token", None)
        st.rerun()
