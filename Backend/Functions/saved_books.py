from Backend.DB_Stuff.db_connect import (
    execute_query_fetch,
    get_connection,
)

def get_saved_books_count(reader_id):

    query = """
    SELECT COUNT(*) AS total
    FROM saved_books
    WHERE Saved_To_Reader_ID = %s
    """

    result = execute_query_fetch(query, (reader_id,))

    return result[0]["total"] if result else 0

def get_saved_books(reader_id):

    query = """
    SELECT
        b.ISBN AS isbn,
        b.Title AS title,
        b.Author AS author,
        b.genre AS genre,
        b.Description AS description,
        COALESCE(b.Average_Rating, 0) AS avg_rating,
        b.Clicked AS clicked,
        b.Saved AS saved,
        b.Publisher AS publisher,
        b.Published_Year AS year,
        b.Cover AS cover,
        b.Review_Count AS review_count

    FROM books AS b

    JOIN saved_books AS sb
        ON sb.Saved_Book_isbn = b.isbn

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

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            INSERT INTO saved_books
            (
                Saved_Book_ISBN,
                Saved_To_Reader_ID
            )
            VALUES (%s, %s)
            """,
            (isbn, saved_to_reader_id),
        )
        cursor.execute(
            """
            UPDATE books
            SET Saved = COALESCE(Saved, 0) + 1
            WHERE ISBN = %s
            """,
            (isbn,),
        )
        connection.commit()

        return {
            "success": True,
            "message": "Book saved successfully"
        }

    except Exception as exc:
        if connection:
            connection.rollback()
        return {
            "success": False,
            "message": f"Book could not be saved: {exc}"
        }

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

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
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            DELETE FROM saved_books
            WHERE Saved_Book_ISBN = %s
            AND Saved_To_Reader_ID = %s
            """,
            (isbn, reader_id),
        )
        deleted_count = cursor.rowcount

        if deleted_count:
            cursor.execute(
                """
                UPDATE books
                SET Saved = GREATEST(COALESCE(Saved, 0) - 1, 0)
                WHERE ISBN = %s
                """,
                (isbn,),
            )

        connection.commit()

        return {
            "success": bool(deleted_count),
            "message": "Saved book removed" if deleted_count else "Saved book was not found"
        }

    except Exception as exc:
        if connection:
            connection.rollback()
        return {
            "success": False,
            "message": f"Saved book could not be removed: {exc}"
        }

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
