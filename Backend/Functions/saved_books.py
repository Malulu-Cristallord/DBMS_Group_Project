from Backend.DB_Stuff.db_connect import (
    execute_query,
    execute_query_fetch
)

def get_saved_books_count(reader_id):

    query = """
    SELECT COUNT(*) AS total
    FROM saved_books
    WHERE Saved_To_Reader_ID = %s
    """

    result = execute_query_fetch(query, (reader_id,))

    return result[0]["total"]

def get_saved_books(reader_id):

    query = """
    SELECT
        b.ISBN,
        b.Title,
        b.Author,
        b.Cover,
        b.Genre,
        b.Average_Rating,
        b.Review_Count,
        b.Clicked

    FROM books AS b

    JOIN saved_books AS sb
        ON sb.Saved_Book_ISBN = b.ISBN

    WHERE sb.Saved_To_Reader_ID = %s
    """

    return execute_query_fetch(query, (reader_id,))

def save_book(isbn, saved_to_reader_id):

    # Prevent duplicates
    if is_book_saved(isbn, saved_to_reader_id):
        return {
            "success": False,
            "message": "Book already saved"
        }

    # Limit check
    saved_count = get_saved_books_count(
        saved_to_reader_id
    )

    if saved_count >= 20:
        return {
            "success": False,
            "message": "Maximum saved books limit reached"
        }

    query = """
    INSERT INTO saved_books
    (
        Saved_Book_ISBN,
        Saved_To_Reader_ID
    )
    VALUES (%s, %s)
    """

    execute_query(
        query,
        (isbn, saved_to_reader_id)
    )

    return {
        "success": True,
        "message": "Book saved successfully"
    }

def is_book_saved(isbn, reader_id):

    query = """
    SELECT 1
    FROM saved_books
    WHERE Saved_Book_ISBN = %s
    AND Saved_To_Reader_ID = %s
    LIMIT 1
    """

    result = execute_query_fetch(
        query,
        (isbn, reader_id)
    )

    return bool(result)

def delete_saved_book(isbn, reader_id):

    query = """
    DELETE FROM saved_books
    WHERE Saved_Book_ISBN = %s
    AND Saved_To_Reader_ID = %s
    """

    execute_query(
        query,
        (isbn, reader_id)
    )

    return {
        "success": True,
        "message": "Saved book removed"
    }