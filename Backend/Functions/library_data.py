from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from Backend.DB_Stuff.db_connect import get_connection


DEFAULT_GENRES = [
    "Fiction",
    "Science fiction",
    "Fantasy",
    "Mystery",
    "Romance",
    "History",
    "Biography",
    "Technology",
]


def fetch_one(query: str, params: tuple[Any, ...] | None = None) -> dict[str, Any] | None:
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        return cursor.fetchone()
    except Exception:
        return None
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def fetch_all(query: str, params: tuple[Any, ...] | None = None) -> list[dict[str, Any]]:
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        return cursor.fetchall()
    except Exception:
        return []
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def execute_write(query: str, params: tuple[Any, ...] | None = None) -> tuple[bool, str]:
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        connection.commit()
        return True, "Saved successfully."
    except Exception as exc:
        if connection:
            connection.rollback()
        return False, f"Database write failed: {exc}"
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def table_exists(table_name: str) -> bool:
    allowed_tables = {"books", "readers", "posts"}
    if table_name not in allowed_tables:
        return False

    row = fetch_one(
        """
        SELECT COUNT(*) AS total
        FROM information_schema.tables
        WHERE table_schema = DATABASE()
          AND table_name = %s
        """,
        (table_name,),
    )
    return bool(row and row.get("total"))


def to_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    if isinstance(value, Decimal):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def reader_initials(name: str | None) -> str:
    if not name:
        return "?"

    words = [part for part in name.strip().split() if part]
    if not words:
        return "?"

    if len(words) == 1:
        return words[0][0].upper()

    return "".join(word[0].upper() for word in words[:2])


def get_reader_by_id(reader_id: int | str | None) -> dict[str, Any] | None:
    if not reader_id:
        return None

    return fetch_one(
        """
        SELECT
            Reader_ID,
            Name,
            Email,
            Preferred_Category,
            Points,
            Receive_Recommendations,
            Show_Reading_History,
            Created_At
        FROM readers
        WHERE Reader_ID = %s
        """,
        (reader_id,),
    )


def get_reader_from_session(session_state: Any) -> dict[str, Any] | None:
    return get_reader_by_id(session_state.get("reader_id"))


def update_reader_profile(
    reader_id: int | str,
    name: str,
    preferred_category: str,
    receive_recommendations: bool,
    show_reading_history: bool,
) -> tuple[bool, str]:
    return execute_write(
        """
        UPDATE readers
        SET
            Name = %s,
            Preferred_Category = %s,
            Receive_Recommendations = %s,
            Show_Reading_History = %s
        WHERE Reader_ID = %s
        """,
        (
            name,
            preferred_category,
            receive_recommendations,
            show_reading_history,
            reader_id,
        ),
    )


def get_reader_genres(reader: dict[str, Any] | None) -> list[str]:
    if not reader or not reader.get("Preferred_Category"):
        return []

    return [
        genre.strip()
        for genre in reader["Preferred_Category"].split(",")
        if genre.strip()
    ]


def get_genres(include_all: bool = True) -> list[str]:
    rows = fetch_all(
        """
        SELECT DISTINCT Category AS category
        FROM books
        WHERE Category IS NOT NULL AND TRIM(Category) <> ''
        ORDER BY Category
        """
    )
    genres = [row["category"] for row in rows if row.get("category")]

    if not genres:
        genres = DEFAULT_GENRES.copy()

    return ["All genres", *genres] if include_all else genres


def normalize_book(row: dict[str, Any]) -> dict[str, Any]:
    rating = to_float(row.get("avg_rating"))
    return {
        "id": row.get("id"),
        "title": row.get("title") or "Untitled",
        "isbn": row.get("isbn") or "",
        "category": row.get("category") or "Uncategorized",
        "publisher": row.get("publisher") or "",
        "year": row.get("year") or "",
        "author": row.get("author") or "Unknown author",
        "cover": row.get("cover") or "#3E7255",
        "description": row.get("description") or "No description has been added yet.",
        "avg_rating": rating,
        "review_count": int(row.get("review_count") or 0),
        "formats": ["Physical"],
    }


def get_books(
    search_query: str = "",
    category: str = "All genres",
    sort_option: str = "rating",
    limit: int | None = None,
) -> list[dict[str, Any]]:
    conditions: list[str] = []
    params: list[Any] = []

    if category and category != "All genres":
        conditions.append("b.Category = %s")
        params.append(category)

    if search_query:
        like_value = f"%{search_query}%"
        conditions.append("(b.Title LIKE %s OR b.Author LIKE %s OR b.Category LIKE %s)")
        params.extend([like_value, like_value, like_value])

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    order_by = "b.Rating DESC, b.Title ASC"
    if sort_option == "title":
        order_by = "b.Title ASC"
    elif sort_option == "year":
        order_by = "b.Published_Year DESC, b.Title ASC"

    limit_clause = ""
    if limit is not None:
        limit_clause = "LIMIT %s"
        params.append(limit)

    if table_exists("posts"):
        rows = fetch_all(
            f"""
            SELECT
                b.Book_ID AS id,
                b.Title AS title,
                b.ISBN AS isbn,
                b.Category AS category,
                b.Publisher AS publisher,
                b.Published_Year AS year,
                b.Author AS author,
                b.Cover AS cover,
                b.Description AS description,
                b.Rating AS avg_rating,
                COUNT(p.Post_ID) AS review_count
            FROM books b
            LEFT JOIN posts p ON p.Book_ID = b.Book_ID
            {where_clause}
            GROUP BY
                b.Book_ID,
                b.Title,
                b.ISBN,
                b.Category,
                b.Publisher,
                b.Published_Year,
                b.Author,
                b.Cover,
                b.Description,
                b.Rating
            ORDER BY {order_by}
            {limit_clause}
            """,
            tuple(params),
        )
    else:
        rows = fetch_all(
            f"""
            SELECT
                b.Book_ID AS id,
                b.Title AS title,
                b.ISBN AS isbn,
                b.Category AS category,
                b.Publisher AS publisher,
                b.Published_Year AS year,
                b.Author AS author,
                b.Cover AS cover,
                b.Description AS description,
                b.Rating AS avg_rating,
                0 AS review_count
            FROM books b
            {where_clause}
            ORDER BY {order_by}
            {limit_clause}
            """,
            tuple(params),
        )

    return [normalize_book(row) for row in rows]


def get_book_by_id(book_id: int | str | None) -> dict[str, Any] | None:
    if not book_id:
        books = get_books(limit=1)
        return books[0] if books else None

    if table_exists("posts"):
        row = fetch_one(
            """
            SELECT
                b.Book_ID AS id,
                b.Title AS title,
                b.ISBN AS isbn,
                b.Category AS category,
                b.Publisher AS publisher,
                b.Published_Year AS year,
                b.Author AS author,
                b.Cover AS cover,
                b.Description AS description,
                b.Rating AS avg_rating,
                COUNT(p.Post_ID) AS review_count
            FROM books b
            LEFT JOIN posts p ON p.Book_ID = b.Book_ID
            WHERE b.Book_ID = %s
            GROUP BY
                b.Book_ID,
                b.Title,
                b.ISBN,
                b.Category,
                b.Publisher,
                b.Published_Year,
                b.Author,
                b.Cover,
                b.Description,
                b.Rating
            """,
            (book_id,),
        )
    else:
        row = fetch_one(
            """
            SELECT
                b.Book_ID AS id,
                b.Title AS title,
                b.ISBN AS isbn,
                b.Category AS category,
                b.Publisher AS publisher,
                b.Published_Year AS year,
                b.Author AS author,
                b.Cover AS cover,
                b.Description AS description,
                b.Rating AS avg_rating,
                0 AS review_count
            FROM books b
            WHERE b.Book_ID = %s
            """,
            (book_id,),
        )

    if row:
        return normalize_book(row)

    books = get_books(limit=1)
    return books[0] if books else None


def get_recommended_books(reader: dict[str, Any] | None, limit: int = 4) -> list[dict[str, Any]]:
    genres = get_reader_genres(reader)

    if not genres:
        return get_books(sort_option="rating", limit=limit)

    books = get_books(sort_option="rating")
    matched_books = [book for book in books if book["category"] in genres][:limit]
    return matched_books or get_books(sort_option="rating", limit=limit)


def get_posts(
    reader_id: int | str | None = None,
    book_id: int | str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    if not table_exists("posts"):
        return []

    conditions: list[str] = []
    params: list[Any] = []

    if reader_id:
        conditions.append("p.Reader_ID = %s")
        params.append(reader_id)

    if book_id:
        conditions.append("p.Book_ID = %s")
        params.append(book_id)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    limit_clause = ""
    if limit is not None:
        limit_clause = "LIMIT %s"
        params.append(limit)

    rows = fetch_all(
        f"""
        SELECT
            p.Post_ID AS post_id,
            p.Reader_ID AS reader_id,
            p.Book_ID AS book_id,
            p.Title AS content,
            p.Rating AS rating,
            p.Upvote_count AS upvote_count,
            p.Created_Date AS created_at,
            r.Name AS reader_name,
            b.Title AS book_title,
            b.Author AS author,
            b.Cover AS cover
        FROM posts p
        LEFT JOIN readers r ON p.Reader_ID = r.Reader_ID
        LEFT JOIN books b ON p.Book_ID = b.Book_ID
        {where_clause}
        ORDER BY p.Created_Date DESC, p.Post_ID DESC
        {limit_clause}
        """,
        tuple(params),
    )

    return rows


def create_post(
    reader_id: int | str,
    book_id: int | str | None,
    content: str,
    rating: int | None = None,
) -> tuple[bool, str]:
    if not table_exists("posts"):
        return False, "The posts table does not exist yet. Run the database setup first."

    clean_content = content.strip()
    if not clean_content:
        return False, "Please write something before publishing."

    return execute_write(
        """
        INSERT INTO posts (
            Title,
            Reader_ID,
            Book_ID,
            Upvote_count,
            Created_Date,
            Rating
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            clean_content[:255],
            reader_id,
            book_id,
            0,
            date.today(),
            rating,
        ),
    )


def get_reader_stats(reader_id: int | str) -> dict[str, Any]:
    if not table_exists("posts"):
        return {
            "posts_published": 0,
            "avg_rating": 0.0,
        }

    row = fetch_one(
        """
        SELECT
            COUNT(Post_ID) AS posts_published,
            AVG(Rating) AS avg_rating
        FROM posts
        WHERE Reader_ID = %s
        """,
        (reader_id,),
    ) or {}

    return {
        "posts_published": int(row.get("posts_published") or 0),
        "avg_rating": round(to_float(row.get("avg_rating")), 1),
    }


def get_platform_stats() -> dict[str, int]:
    readers = fetch_one("SELECT COUNT(*) AS total FROM readers") or {}
    books = fetch_one("SELECT COUNT(*) AS total FROM books") or {}
    posts = fetch_one("SELECT COUNT(*) AS total FROM posts") if table_exists("posts") else {}

    return {
        "active_readers": int(readers.get("total") or 0),
        "borrowings_this_month": 0,
        "reviews_published": int(posts.get("total") or 0),
        "available_titles": int(books.get("total") or 0),
    }


def get_leaderboard(current_reader_id: int | str | None = None, limit: int = 10) -> list[dict[str, Any]]:
    rows = fetch_all(
        """
        SELECT
            Reader_ID,
            Name,
            Points,
            Created_At
        FROM readers
        ORDER BY Points DESC, Created_At ASC
        LIMIT %s
        """,
        (limit,),
    )

    leaderboard = []
    for rank, row in enumerate(rows, start=1):
        points = int(row.get("Points") or 0)
        leaderboard.append(
            {
                "rank": rank,
                "reader_id": row.get("Reader_ID"),
                "reader_name": row.get("Name") or "Unknown reader",
                "initials": reader_initials(row.get("Name")),
                "points": points,
                "is_current_reader": str(row.get("Reader_ID")) == str(current_reader_id),
                "badge": "Gold" if rank == 1 else ("Silver" if rank == 2 else "Bronze" if rank == 3 else ""),
            }
        )

    return leaderboard


def get_reader_badges(reader: dict[str, Any] | None, posts_published: int = 0) -> list[dict[str, Any]]:
    points = int((reader or {}).get("Points") or 0)
    genres = get_reader_genres(reader)

    return [
        {
            "name": "Active reader",
            "description": "Reach 25 reader points",
            "earned": points >= 25,
            "progress": min(100, int((points / 25) * 100)) if points else 0,
        },
        {
            "name": "Community reviewer",
            "description": "Publish 3 posts or reviews",
            "earned": posts_published >= 3,
            "progress": min(100, int((posts_published / 3) * 100)) if posts_published else 0,
        },
        {
            "name": "Genre explorer",
            "description": "Choose at least 3 preferred genres",
            "earned": len(genres) >= 3,
            "progress": min(100, int((len(genres) / 3) * 100)) if genres else 0,
        },
    ]
    if not table_exists("posts"):
        return False, "The posts table does not exist yet. Run the database setup first."
