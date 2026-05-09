import requests
from mysql.connector import IntegrityError
from requests import RequestException

from Backend.DB_Stuff import db_connect


def extract_categories(book_data):
    raw_subjects = book_data.get("subjects", [])

    # clean categories (remove "-- Juvenile fiction" suffix)
    cleaned = []
    for s in raw_subjects:
        cleaned.append(s.split(" -- ")[0].strip())

    return cleaned

headers = {
    'User-Agent': 'LibTrack(malucristallord@gmail.com)'
}

def data_to_db(book_data, author_data):
    print("data to db")

    # Data extraction
    try:

        title = book_data.get("title", "")
        isbn = book_data.get("isbn_13", [""])[0]
        category = extract_categories(book_data)
        author_name = author_data.get("personal_name", "Unknown")
        rating = 0

        description = book_data.get("description", "")
        if isinstance(description, dict):
            description = description.get("value", "")

        publisher = book_data.get("publishers", [""])[0]
        published_year = book_data.get("publish_date", "")[-4:]

        query = """
        INSERT IGNORE INTO books
        (Title, ISBN, Author, Rating, Description, Publisher, Published_Year)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            title,
            isbn,
            author_name,
            rating,
            description[:255] if description else "",
            publisher,
            published_year if published_year.isdigit() else None,
        )
        print("values:", values)

        db_connect.insert_book(query, values)

        category_query = """
        INSERT INTO  book_categories (ISBN, Category)
        VALUES (%s, %s)
        """
        print("category_query:", category_query)
        for category in category:
            db_connect.execute_query(category_query, (isbn, category))

        print("insertion complete")

    except IntegrityError as e:
        print(f"IntegrityError: {e}")
    except RequestException as e:
        print(f"RequestException: {e}")
    except ValueError as e:
        print(f"ValueError: {e}")
    except Exception  as e:
        print(f"Unknown general error: {e}")

def request_book_data(isbn_value):
    try:
        print("requesting book data")
        book_api = f"https://openlibrary.org/isbn/{isbn_value}.json"
        book_response = requests.get(book_api, timeout=10, headers=headers)
        book_response.raise_for_status()
        book_data = book_response.json()
        print("Book data: ", book_data)

        author_id = book_data["authors"][0]["key"]
        author_api = f"https://openlibrary.org{author_id}.json"
        author_response = requests.get(author_api, timeout=10, headers=headers)
        author_response.raise_for_status()
        author_data = author_response.json()

        if book_data is None:
            print("Failed to fetch data, trying to fetch from backup online database")

        data_to_db(book_data, author_data)
        return book_data

    except KeyError as exc:
        return {"error": f"Unable to retrieve data for ISBN {isbn_value}: {exc}"}
    except RequestException as e:
        print(f"RequestException: {e}")
    except Exception as e:
        print(f"Unknown general error: {e}")


def request_book_data_alt(isbn_value):
    return None


def test():
    print("Test phase, input = 9780439362139")
    request_book_data("9780439362139")

test()