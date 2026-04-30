import streamlit as st


st.set_page_config(
    page_title="LibTrack",
    page_icon="LT",
    layout="wide",
)

st.info("This legacy entry point has moved to the reader-focused LibTrack app.")

if st.button("Open LibTrack"):
    st.switch_page("app.py")
