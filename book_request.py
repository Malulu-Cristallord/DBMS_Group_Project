import requests

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
    # Gather title, bookID, ISBN, Category, Author, Description, publisher, PublishedYear
    title = book_data["title"]
    isbn = book_data["isbn_13"]
    category = format_subjects(book_data)
    author_name = author_data["personal_name"]
    rating = 0
    description = book_data["description"]
    publisher = book_data["publishers"]
    published_year = book_data["published_year"]

    try:
        query = (f"INSERT INTO Books_Global"
                 f"(Title, ISBN, Category, Author, AuthorName, Rating, Description, Publisher, Published_Year)")
        values = f"{title}, {isbn}, {category}, {author_name}, {rating}, {description}, {publisher}, {published_year:%Y}"
        db_connect.insert_book(query, values)
        return f"Query: {query}"

    except KeyError:
        return "Error occurred while inserting data into database"



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

        return data_to_db(book_data, author_data)
        # Test stat = 9780439362139 (Harry Potter 1)

    except Exception:
        return "Unable to retrieve data. Check the ISBN number."