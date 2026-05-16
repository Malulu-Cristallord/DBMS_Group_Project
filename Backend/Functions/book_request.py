import requests
from mysql.connector import IntegrityError
from requests import RequestException

from Backend.DB_Stuff import db_connect


headers = {
    'User-Agent': 'LibTrack(malucristallord@gmail.com)'
}

def data_to_db(book_data, author_data, gathered_at):
    print("data to db")

    # Data extraction
    try:

        title = book_data.get("title", "")
        isbn = book_data.get("isbn_13", [""])[0]
        author_name = author_data.get("personal_name", "Unknown") if author_data else ""

        cover_data = book_data.get("covers", [])
        genre = book_data.get("genre", "Uncategorized")
        cover = (
            f"https://covers.openlibrary.org/b/id/{cover_data[0]}-L.jpg"
            if cover_data
            else None
        )

        description = book_data.get("description", "")
        if isinstance(description, dict):
            description = description.get("value", "")

        publisher = book_data.get("publishers", [""])[0]
        published_year = book_data.get("publish_date", "")[-4:]

        query = """
        INSERT IGNORE INTO books
        (Title, ISBN, Author, Description, Publisher, Published_Year, cover, Genre, Gathered_At)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            title,
            isbn,
            author_name,
            description[:255] if description else "",
            publisher,
            published_year if published_year.isdigit() else None,
            cover,
            genre,
            gathered_at
        )
        print("values:", values)

        db_connect.insert_book(query, values)


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
        gathered_at = "Open Library"

        if book_data is None:
            print("Failed to fetch data, trying to fetch from backup online database")
            raise RequestException

        print("Book data: ", book_data)

        author_data = None
        authors = book_data.get("authors", [])

        if authors and isinstance(authors, list):
            try:
                author_id = authors[0].get("key")

                if author_id:
                    author_api = f"https://openlibrary.org{author_id}.json"

                    author_response = requests.get(
                        author_api,
                        timeout=10,
                        headers=headers
                    )

                    author_response.raise_for_status()

                    author_data = author_response.json()

            except RequestException as e:
                print(f"Failed to retrieve author data: {e}")

            except Exception as e:
                print(f"Unexpected author retrieval error: {e}")

        data_to_db(book_data, author_data, gathered_at)
        return book_data

    except KeyError as exc:
        return {"error": f"Unable to retrieve data for ISBN {isbn_value}: {exc}"}
    except RequestException as e:
        print(f"RequestException: {e}")
    except Exception as e:
        print(f"Unknown general error: {e}")

def get_book_cover(isbn_value):
    try:
        print("requesting book image")
        query = """SELECT Cover FROM books
        WHERE ISBN = %s"""
        values = (isbn_value,)
        result = db_connect.execute_query_fetch(query, values)

        if result and len(result) > 0:
            return result[0]["Cover"]  # extract actual image
        return None

    except Exception as e:
        print(f"Exception: {e}")


def request_book_data_google(isbn_value):
    try:
        print("Requesting Google Books data")

        api = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn_value}"

        response = requests.get(
            api,
            timeout=10,
            headers=headers
        )

        response.raise_for_status()

        data = response.json()

        # No books found
        if data.get("totalItems", 0) == 0:
            return {
                "error": f"No book found for ISBN {isbn_value}"
            }

        # First matched book
        book_data = data["items"][0]

        print("Book data:", book_data)

        data_to_db(book_data)

        return book_data

    except RequestException as e:
        print(f"RequestException: {e}")
        return {"error": str(e)}

    except Exception as e:
        print(f"Unknown general error: {e}")
        return {"error": str(e)}

def get_book_cover_google(isbn_value):
    try:
        query = """
            SELECT Cover
            FROM books
            WHERE ISBN = %s
            """

        values = (isbn_value,)

        result = db_connect.execute_query_fetch(query, values)

        if result and len(result) > 0:
            return result[0]["Cover"]

        return None

    except Exception as e:
        print(f"Exception: {e}")


def test():
    print("Test phase, input = 978043936213")
    request_book_data("9780439362139")
