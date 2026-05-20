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

def get_post_by_id(post_id):
    query = """
    SELECT Post_ID, Content, Created_Date, Reader_ID, ISBN
    FROM posts
    WHERE Post_ID = %s
    """
    return fetch_all(query, (post_id,))

def get_book_by_isbn(isbn):
    book_query = """
    SELECT Title, ISBN, Publisher, Published_Year, Author, Description, Cover, Average_Rating, Review_Count
    FROM books
    WHERE ISBN = %s
    """

    category_query = """
    SELECT Category
    FROM book_categories
    WHERE ISBN = %s
    """

    rows = fetch_all(book_query, (isbn,))
    print("DEBUG ROWS:", rows)

    if not rows:
        return None

    row = rows[0]

    category_rows = fetch_all(category_query, (isbn,))
    categories = [c["Category"] for c in category_rows] if category_rows else []

    return {
        "Title": row["Title"],
        "ISBN": row["ISBN"],
        "publisher": row["Publisher"],
        "year": row["Published_Year"],
        "Author": row["Author"],
        "description": row["Description"],
        "cover": row["Cover"],
        "categories": categories,
        "avg_rating": row["Average_Rating"],
        "review_count": row["Review_Count"]
    }


def update_post(
    post_id: int | str,
    content: str,
    isbn: str | None = None,
    ) -> tuple[bool, str]:

    if not table_exists("posts"):
        return False, "The posts table does not exist."

    clean_content = content.strip()

    if not clean_content:
        return False, "Post content cannot be empty."

    query = """
    UPDATE posts
    SET
        Content = %s,
        ISBN = %s
    WHERE Post_ID = %s
    """

    values = (
        clean_content[:255],
        isbn,
        post_id
    )

    return execute_write(query, values)
