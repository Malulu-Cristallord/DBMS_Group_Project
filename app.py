import streamlit as st

import book_request


def update_isbn():
    isbn = st.session_state.user_input
    book_request.request_book_data(isbn)
    st.session_state.book_data = book_request.request_book_data_with_returning_value(isbn)


if 'book_data' not in st.session_state:
    st.session_state.counter = ''

st.header("type in the isbn and the system will find the book from open library!")
st.text_input(label="ISBN", key='user_input', placeholder="Enter ISBN")
st.button(label="Submit",on_click=update_isbn)
st.text_area(label="Book data", key='book_data', placeholder="Will show book data here", height=2000)

# Front end to be edited