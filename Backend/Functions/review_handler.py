from typing import Any

from Backend.DB_Stuff.db_connect import execute_query
from Backend.Functions.library_data import fetch_all, fetch_one, table_exists, update_book_review_stats


def create_review(
    reader_id: int | str,
    isbn: str,
    content: str,
    rating: int,
) -> tuple[bool, str]:
    if not table_exists("reviews"):
        return False, "The reviews table does not exist yet. Run the database setup first."

    clean_content = content.strip()

    if not clean_content:
        return False, "Please write something before publishing."

    # 先找有沒有評論過
    check_query = """
    SELECT review_id
    FROM reviews
    WHERE reader_id = %s AND isbn = %s
    """

    existing = fetch_one(check_query, (reader_id, isbn))

    # 已存在 -> UPDATE
    if existing:
        update_query = """
        UPDATE reviews
        SET content = %s,
            rating = %s
        WHERE review_id = %s
        """

        execute_query(
            update_query,
            (clean_content, rating, existing["review_id"])
        )
        update_book_review_stats(isbn)
        return True, "Your review has been updated."

    # 不存在 -> INSERT
    insert_query = """
    INSERT INTO reviews (
        reader_id,
        isbn,
        content,
        rating
    )
    VALUES (%s, %s, %s, %s)
    """

    execute_query(
        insert_query,
        (reader_id, isbn, clean_content, rating)
    )
    update_book_review_stats(isbn)
    return True, "Review published successfully."


def get_reviews(
    reader_id: int | str | None = None,
    isbn: int | str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    if not table_exists("reviews"):
        return []

    conditions: list[str] = []
    params: list[Any] = []

    if reader_id:
        conditions.append("r.Reader_ID = %s")
        params.append(reader_id)

    if isbn:
        conditions.append("r.ISBN = %s")
        params.append(isbn)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    limit_clause = ""
    if limit is not None:
        limit_clause = "LIMIT %s"
        params.append(limit)

    rows = fetch_all(
        f"""
        SELECT
            r.Review_ID AS review_id,
            r.Reader_ID AS reader_id,
            r.ISBN AS isbn,
            r.Content AS content,
            r.Rating AS rating,
            r.Created_At AS created_at,
            rd.Name AS reader_name,
            b.Title AS book_title,
            b.Author AS author,
            b.Cover AS cover
        FROM reviews r
        LEFT JOIN readers rd ON r.Reader_ID = rd.Reader_ID
        LEFT JOIN books b ON r.ISBN = b.ISBN
        {where_clause}
        ORDER BY r.Created_At DESC, r.Review_ID DESC
        {limit_clause}
        """,
        tuple(params),
    )

    return rows

def get_review_by_reader_and_book(reader_id, isbn):

    query = """
    SELECT *
    FROM reviews
    WHERE Reader_ID = %s
    AND ISBN = %s
    """

    return fetch_one(query, (reader_id, isbn))