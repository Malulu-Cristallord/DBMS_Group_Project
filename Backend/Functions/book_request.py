import requests
from mysql.connector import IntegrityError
from requests import RequestException

from Backend.DB_Stuff import db_connect
from Backend.DB_Stuff.db_connect import execute_query, execute_query_fetch

headers = {
    'User-Agent': 'LibTrack(malucristallord@gmail.com)'
}

# Workflow: input isbn > search the db for duplicates > request data from Open Library > data to db
# If failed on request from Ol > request data from Google Books


def data_to_db(book_data, author_data, gathered_at):
    print("data to db")

    # Data extraction
    try:

        title = book_data.get("title", "")
        isbn = book_data.get("isbn_13", [""])[0]
        author_name = author_data.get("personal_name", "Unknown") if author_data else ""

        cover_data = book_data.get("covers", [])
        genre = book_data.get("genres")[0] if book_data.get("genres") else "Uncategorized"
        print(f"Found genre: {genre}")
        cover = (
            f"https://covers.openlibrary.org/b/id/{cover_data[0]}-L.jpg"
            if cover_data
            else "Resources/Book Covers/Cover_Default.png"
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

def check_duplicates(isbn_value):
    query = f"""
    -- webb: Use the actual lowercase books table name from the schema.
    SELECT COUNT(*) AS count FROM books WHERE ISBN = %s
    """
    values = (isbn_value,)
    result = execute_query_fetch(query, values)
    # Example result:
    # [{'count': 0}]

    count = result[0]["count"]
    print(count)
    print(f"duplicates count: {count}")

    if count == 0:
        print("No duplicates found")
        return True
    else:
        print("Duplicates found")
        return False

def request_book_data(isbn_value):
    if check_duplicates(isbn_value):
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
            print({"error": f"Unable to retrieve data for ISBN {isbn_value}: {exc}"})
            return "error"
        except RequestException as e:
            print(f"RequestException: {e}")
            return "error"
        except Exception as e:
            print(f"Unknown general error: {e}")
            return "error"
    else:
        print(f"Book data for ISBN {isbn_value} already exists")
        return -1


def get_book_cover(isbn_value) -> str:
    try:
        query = """SELECT Cover FROM books
        WHERE ISBN = %s"""
        values = (isbn_value,)
        result = db_connect.execute_query_fetch(query, values)

        if result and len(result) > 0:
            return str(result[0]["Cover"])  # extract actual image

    except Exception as e:
        print(f"Exception: {e}")


def test():
    print("Test phase, input = 978043936213")
    request_book_data("9780439362139")

def increment_add_books(reader_ID):
    print("Increment add books phase for readerID ", reader_ID)
    try:
        query = """
        UPDATE readers
        SET Books_Added = Books_Added + 1
        WHERE reader_ID = %s
        """
        values = (reader_ID,)
        db_connect.execute_query(query, values)
    except RequestException as e:
        print(f"RequestException: {e}")
    except Exception as e:
        print(f"Unknown general error: {e}")

def check_for_badge_book_adding(reader_ID):
    query = f"""
    SELECT Books_Added FROM readers
    WHERE reader_ID = %s
    """
    values = (reader_ID,)
    result = execute_query_fetch(query, values)
    if result and len(result) > 0:
        if 10 <= result[0]["Books_Added"] < 50:
            return 'badge_add_books_01'
        elif 50 <= result[0]["Books_Added"] < 200:
            return 'badge_add_books_02'
        elif 200 <= result[0]["Books_Added"] < 500:
            return 'badge_add_books_03'
        elif result[0]["Books_Added"] >= 500:
            return 'badge_add_books_04'
        else:
            return None
    return None
