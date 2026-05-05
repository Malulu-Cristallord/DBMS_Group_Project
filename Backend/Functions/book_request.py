import requests
from requests import RequestException

from Backend.DB_Stuff import db_connect


def format_subjects(book_data):
    subjects = book_data.get("subjects", [])
    return " / ".join(subjects) if subjects else "None"


def data_to_db(book_data, author_data):
    print("data to db")
    title = book_data.get("title", "")
    isbn = book_data.get("isbn_13", [""])[0]
    category = format_subjects(book_data)
    author_name = author_data.get("personal_name", "Unknown")
    rating = 0

    description = book_data.get("description", "")
    if isinstance(description, dict):
        description = description.get("value", "")

    publisher = book_data.get("publishers", [""])[0]
    published_year = book_data.get("publish_date", "")[-4:]

    query = """
    INSERT IGNORE INTO books
    (Title, ISBN, Category, Author, Rating, Description, Publisher, Published_Year)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        title,
        isbn,
        category,
        author_name,
        rating,
        description[:255] if description else "",
        publisher,
        published_year if published_year.isdigit() else None,
    )
    print("values:", values)

    return db_connect.insert_book(query, values)


def request_book_data(isbn_value):
    try:
        book_api = f"https://openlibrary.org/isbn/{isbn_value}.json"
        book_response = requests.get(book_api, timeout=10)
        book_response.raise_for_status()
        book_data = book_response.json()

        author_id = book_data["authors"][0]["key"]
        author_api = f"https://openlibrary.org{author_id}.json"
        author_response = requests.get(author_api, timeout=10)
        author_response.raise_for_status()
        author_data = author_response.json()

        if book_data is None:
            print("Failed to fetch data, trying to fetch from backup online database")


        data_to_db(book_data, author_data)
        return book_data

    except KeyError as exc:
        return {"error": f"Unable to retrieve data for ISBN {isbn_value}: {exc}"}


def request_book_data_alt(isbn_value):
    return None


def test():
    print("Test phase, input = 9780141346809")
    request_book_data("9780141346809")
