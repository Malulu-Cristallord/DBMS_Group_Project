import streamlit as st


def my_callback():
    st.session_state.counter += 1

if 'counter' not in st.session_state:
    st.session_state.counter = 0

st.header("type in the isbn and the system will find the book from open library!")
st.text_input(label="ISBN", placeholder="Enter ISBN")
st.button(label="Submit",on_click=my_callback)