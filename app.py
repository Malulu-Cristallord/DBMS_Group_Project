import streamlit as st
import book_request


# Init session_state:
if 'book_data' not in st.session_state:
    st.session_state.book_data = ""

# Callback function
def update_isbn():
    isbn = st.session_state.user_input.strip()

    if not isbn:
        st.session_state.book_data = "Please enter a valid ISBN."
        return

    # Show loading feedback while blocking operations run
    with st.spinner("Fetching book data..."):
        result = book_request.request_book_data(isbn)

    st.session_state.book_data = result


# UI layout
st.header("Enter an ISBN to fetch book data from Open Library")

st.text_input(
    label="ISBN",
    key='user_input',
    placeholder="e.g. 9780439362139"
)

st.button(
    label="Submit",
    on_click=update_isbn
)

st.text_area(
    label="Book data",
    value=st.session_state.book_data,
    height=500
)