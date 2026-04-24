import requests
import json

import db_connect

# Notes: The current db source, Open Library, is still our best choice when it comes to fetching books.
# However, the db seems to have a major lack of books in Asian language.
# I will try to use more APIs if possible, and keep them free cause even the biggest dbs I can find still have big holes in them.
# -Malu

# Formatting data
def format_subjects(book_data):
    try:
        subjects_list = book_data["subjects"]
        subjects_str = " / ".join(subjects_list)
        return subjects_str
    except KeyError:
        return "None"

def data_to_db(book_data, author_data):
    try:
        title = book_data.get("title", "")
        isbn = book_data.get("isbn_13", [""])[0]
        category = " "
        author_name = author_data.get("personal_name", "Unknown")
        rating = 0

        description = book_data.get("description", "")
        if isinstance(description, dict):
            description = description.get("value", "")

        publisher = book_data.get("publishers", [""])[0]
        published_year = book_data.get("publish_date","%Y")

        query = """
        INSERT INTO Books
        (Title, ISBN, Category, Author, Rating, Description, Publisher, Published_Year)
        VALUES (%s, %s, %s, %s, %d, %s, %s, %s)
        """

        values = (
            title,
            isbn,
            category,
            author_name,
            rating,
            description,
            publisher,
            published_year
        )

        db_connect.insert_book(query, values)
        print(f"trying to insert: {query}\n{values}")

    except Exception as e:
        print("Error occurred while inserting data:", e)


def request_book_data(user_input):

    # Gather data with api
    try:
        book_api = f"https://openlibrary.org/isbn/{user_input}.json"
        book_response = requests.get(book_api)
        book_data = book_response.json()
        author_id = book_data["authors"][0]["key"]
        author_api = f"https://openlibrary.org{author_id}.json"
        author_response = requests.get(author_api, timeout=5)
        author_data = author_response.json()
        print(book_api)
        print(book_data)
        print(author_api)
        print(author_data)
        data_to_db(book_data, author_data)
        # Test stat = 9780439362139 (Harry Potter 1)

    except KeyError:
        return "Unable to retrieve data. Check the ISBN number."