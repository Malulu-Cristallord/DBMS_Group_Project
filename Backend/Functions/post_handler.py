from Backend.DB_Stuff.db_connect import fetch_all, execute_query
from Backend.Functions.library_data import table_exists, execute_write


def create_post(
    reader_id: int | str,
    isbn: str | None = None,
    content: str = "",
    book_id: int | str | None = None,
) -> tuple[bool, str]:
    if not table_exists("posts"):
        return False, "The posts table does not exist yet. Run the database setup first."

    if isbn is None and book_id is not None:
        isbn = str(book_id)

    clean_content = content.strip()
    if not clean_content:
        return False, "Please write something before publishing."

    return execute_write(
        """
        INSERT INTO posts (
            Content,
            Created_Date,
            Reader_ID,
            ISBN
        )
        VALUES (%s, CURRENT_TIMESTAMP, %s, %s)
        """,
        (
            clean_content[:255],
            reader_id,
            isbn,
        ),
    )

def get_posts_by_reader(reader_id):

    query = """
    SELECT
        p.Post_ID,
        p.Content,
        p.Created_Date,

        b.Title

    FROM posts p

    LEFT JOIN books b
        ON p.ISBN = b.ISBN

    WHERE p.Reader_ID = %s

    ORDER BY p.Created_Date DESC
    """

    return fetch_all(query, (reader_id,))

def delete_post(post_id):

    query = """
    DELETE FROM posts
    WHERE Post_ID = %s
    """

    execute_query(query, (post_id,))

    return True, "Post deleted successfully."