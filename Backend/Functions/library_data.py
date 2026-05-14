from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from Backend.DB_Stuff import db_connect
from Backend.DB_Stuff.db_connect import execute_query, get_connection


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
    allowed_tables = {
        "books",
        "readers",
        "posts",
        "reviews",
        "recommendations",
        "likes",
        "comments",
        "badges",
        "rewards",
    }
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

    reader = fetch_one(
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

    if reader:
        reader["reader_id"] = reader.get("Reader_ID")
        reader["name"] = reader.get("Name")
        reader["email"] = reader.get("Email")
        reader["preferred_category"] = reader.get("Preferred_Category")
        reader["point"] = reader.get("Points")

    return reader


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
        "id": row.get("id") or row.get("isbn"),
        "title": row.get("title") or "Untitled",
        "isbn": row.get("isbn") or "",
        "genre": row.get("genre") or "Uncategorized",
        "publisher": row.get("publisher") or "",
        "year": row.get("year") or "",
        "author": row.get("author") or "Unknown author",
        "cover": row.get("cover") or "#3E7255",
        "description": row.get("description") or "No description has been added yet.",
        "avg_rating": rating,
        "clicked": int(row.get("clicked") or 0),
        "saved": int(row.get("saved") or 0),
        "review_count": int(row.get("review_count") or 0),
        "score": to_float(row.get("score")),
        "reason": row.get("reason") or "",
        "recommendation_status": row.get("recommendation_status") or row.get("status") or "",
        "generated_at": row.get("generated_at"),
        "formats": ["Physical"],
    }


def get_books(
    search_query: str = "",
    genre: str = "All genres",
    sort_option: str = "rating",
    limit: int | None = None,
    ) -> list[dict[str, Any]]:
    conditions: list[str] = []
    params: list[Any] = []

    if genre and genre != "All genres":
        conditions.append("b.genre = %s")
        params.append(genre)

    if search_query:
        like_value = f"%{search_query}%"
        conditions.append("(b.Title LIKE %s OR b.Author LIKE %s OR b.genre LIKE %s)")
        params.extend([like_value, like_value, like_value])

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    order_by = "b.Average_Rating DESC, b.Title ASC"
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
                b.ISBN AS isbn,
                b.Title AS title,
                b.genre AS genre,
                b.Publisher AS publisher,
                b.Published_Year AS year,
                b.Author AS author,
                b.Cover AS cover,
                b.Description AS description,
                COALESCE(b.Average_Rating, 0) AS avg_rating,
                b.Clicked AS clicked,
                b.Saved AS saved,
                b.Review_Count AS review_count
            FROM books b
            {where_clause}
            GROUP BY
                b.Title,
                b.ISBN,
                b.Publisher,
                b.Published_Year,
                b.Author,
                b.Cover,
                b.Description,
                b.Average_Rating,
                b.Clicked,
                b.Saved
            ORDER BY {order_by}
            {limit_clause}
            """,
            tuple(params),
        )
    else:
        rows = fetch_all(
            f"""
            SELECT
                b.ISBN AS id,
                b.Title AS title,
                b.ISBN AS isbn,
                b.Publisher AS publisher,
                b.Published_Year AS year,
                b.Author AS author,
                b.Cover AS cover,
                b.Description AS description,
                COALESCE(b.Average_Rating, 0) AS avg_rating,
                b.Clicked AS clicked,
                b.Saved AS saved,
                0 AS review_count
            FROM books b
            {where_clause}
            ORDER BY {order_by}
            {limit_clause}
            """,
            tuple(params),
        )

    return [normalize_book(row) for row in rows]

#this is not use now below has a function has the same name but different code.
def get_book_by_isbn(book_isbn: int | str | None) -> dict[str, Any] | None:
    if not book_isbn:
        books = get_books(limit=1)
        return books[0] if books else None
    row = fetch_one(
        """
            SELECT
            b.ISBN AS isbn,
            b.Title AS title,
            b.Genre AS genre,
            b.Publisher AS publisher,
            b.Published_Year AS year,
            b.Author AS author,
            b.Cover AS cover,
            b.Description AS description,
            COALESCE(b.Average_Rating, 0) AS avg_rating,
            b.Clicked AS clicked,
            b.Saved AS saved,
            b.Review_Count AS review_count
            FROM books b
            WHERE b.ISBN = %s
            GROUP BY b.ISBN
            """,
            (book_isbn,),
        )
    if row:
        return normalize_book(row)

    books = get_books(limit=1)
    return books[0] if books else None


def _category_matches(book_category: str | None, reader: dict[str, Any] | None) -> bool:
    preferred_categories = {genre.casefold() for genre in get_reader_genres(reader)}
    if not preferred_categories:
        return False

    return (book_category or "").strip().casefold() in preferred_categories


def _recommendation_reason(book: dict[str, Any], reader: dict[str, Any] | None) -> str:
    if _category_matches(book.get("genre"), reader) and int(book.get("saved") or 0) > 0:
        return "Recommended because it matches your preferred genre and has strong reader engagement."
    if _category_matches(book.get("genre"), reader):
        return f"Recommended because this book matches your preferred genre: {book.get('genre')}."
    if to_float(book.get("avg_rating")) >= 4:
        return "Recommended because it has a high rating and many readers saved it."
    return "Recommended because it has a strong overall recommendation score."


def get_books_for_recommendation() -> list[dict[str, Any]]:
    rows = fetch_all(
        """
        SELECT
            b.ISBN AS id,
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
        FROM books b
        """
    )

    books = [normalize_book(row) for row in rows]
    max_clicked = max([book["clicked"] for book in books], default=0)
    max_saved = max([book["saved"] for book in books], default=0)

    for book in books:
        book["_max_clicked"] = max_clicked
        book["_max_saved"] = max_saved

    return books


def calculate_recommendation_score(book: dict[str, Any], reader: dict[str, Any] | None) -> float:
    rating_weight = 0.4
    clicked_weight = 0.2
    saved_weight = 0.2
    category_weight = 0.2

    normalized_rating = max(0.0, min(1.0, to_float(book.get("rating")) / 5))

    max_clicked = int(book.get("_max_clicked") or 0)
    normalized_clicked = (int(book.get("clicked") or 0) / max_clicked) if max_clicked else 0.0

    max_saved = int(book.get("_max_saved") or 0)
    normalized_saved = (int(book.get("saved") or 0) / max_saved) if max_saved else 0.0

    category_match = 1.0 if _category_matches(book.get("genre"), reader) else 0.0

    score = (
        rating_weight * normalized_rating
        + clicked_weight * normalized_clicked
        + saved_weight * normalized_saved
        + category_weight * category_match
    )
    return round(score, 4)


def _rank_recommendation_candidates(
    books: list[dict[str, Any]],
    reader: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    for book in books:
        book["score"] = calculate_recommendation_score(book, reader)
        book["reason"] = _recommendation_reason(book, reader)

    preferred_books = [book for book in books if _category_matches(book.get("genre"), reader)]
    other_books = [book for book in books if not _category_matches(book.get("genre"), reader)]

    preferred_books.sort(key=lambda book: (book["score"], to_float(book.get("rating"))), reverse=True)
    other_books.sort(key=lambda book: (book["score"], to_float(book.get("rating"))), reverse=True)

    return preferred_books + other_books


def generate_recommendations_for_reader(reader_id: int | str, limit: int = 10) -> list[dict[str, Any]]:
    if not table_exists("recommendations"):
        return []

    reader = get_reader_by_id(reader_id)
    if not reader:
        return []

    books = get_books_for_recommendation()
    candidates = _rank_recommendation_candidates(books, reader)[:limit]

    for book in candidates:
        execute_write(
            """
            INSERT IGNORE INTO recommendations (
                Reader_ID,
                ISBN,
                Score,
                Reason,
                Generated_At,
                Status
            )
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, 'unread')
            """,
            (
                reader_id,
                book["isbn"],
                book["score"],
                book["reason"],
            ),
        )

    return get_recommendations_for_reader(reader_id, limit=limit)


def get_recommendations_for_reader(
    reader_id: int | str,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    if not table_exists("recommendations"):
        return []

    params: list[Any] = [reader_id]
    limit_clause = ""
    if limit is not None:
        limit_clause = "LIMIT %s"
        params.append(limit)

    rows = fetch_all(
        f"""
        SELECT
            rec.Recommendation_ID AS recommendation_id,
            rec.ISBN AS id,
            rec.ISBN AS isbn,
            rec.Score AS score,
            rec.Reason AS reason,
            rec.Generated_At AS generated_at,
            rec.Status AS recommendation_status,
            b.Title AS title,
            b.Author AS author,
            b.genre AS genre,
            b.Description AS description,
            b.Publisher AS publisher,
            b.Published_Year AS year,
            b.Cover AS cover,
            COALESCE(b.Average_Rating, 0) AS avg_rating,
            b.Clicked AS clicked,
            b.Saved AS saved,
            b.Review_Count AS review_count
        FROM recommendations rec
        JOIN books b ON rec.ISBN = b.ISBN
        WHERE rec.Reader_ID = %s
        ORDER BY rec.Score DESC, rec.Generated_At DESC
        {limit_clause}
        """,
        tuple(params),
    )

    return [normalize_book(row) | {"recommendation_id": row.get("recommendation_id")} for row in rows]


def update_recommendation_status(
    reader_id: int | str,
    book_isbn: int | str,
    status: str,
) -> tuple[bool, str]:
    allowed_statuses = {"unread", "clicked", "saved"}
    if status not in allowed_statuses:
        return False, "Invalid recommendation status."

    return execute_write(
        """
        UPDATE recommendations
        SET Status = %s
        WHERE Reader_ID = %s
          AND ISBN = %s
        """,
        (status, reader_id, book_isbn),
    )


def increment_book_clicked(book_isbn: int | str) -> tuple[bool, str]:
    return execute_write(
        """
        UPDATE books
        SET Clicked = COALESCE(Clicked, 0) + 1
        WHERE ISBN = %s
        """,
        (book_isbn,),
    )


def increment_book_saved(book_isbn: int | str) -> tuple[bool, str]:
    return execute_write(
        """
        UPDATE books
        SET Saved = COALESCE(Saved, 0) + 1
        WHERE ISBN = %s
        """,
        (book_isbn,),
    )


def get_recommended_books(reader: dict[str, Any] | None, limit: int = 4) -> list[dict[str, Any]]:
    books = get_books_for_recommendation()
    if not books:
        return get_books(sort_option="rating", limit=limit)

    return _rank_recommendation_candidates(books, reader)[:limit]


def get_posts(
    reader_id: int | str | None = None,
    book_isbn: int | str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    if not table_exists("posts"):
        return []

    conditions: list[str] = []
    params: list[Any] = []

    if reader_id:
        conditions.append("p.Reader_ID = %s")
        params.append(reader_id)

    if book_isbn:
        conditions.append("p.ISBN = %s")
        params.append(book_isbn)

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
            p.ISBN AS isbn,
            p.Content AS content,
            p.Created_Date AS created_at,
            r.Name AS reader_name,
            b.Title AS book_title,
            b.Author AS author,
            b.Cover AS cover
        FROM posts p
        LEFT JOIN readers r ON p.Reader_ID = r.Reader_ID
        LEFT JOIN books b ON p.ISBN = b.ISBN
        {where_clause}
        ORDER BY p.Created_Date DESC, p.Post_ID DESC
        {limit_clause}
        """,
        tuple(params),
    )

    return rows




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


def get_reader_stats(reader_id: int | str) -> dict[str, Any]:
    if not table_exists("posts"):
        return {
            "posts_published": 0,
            "avg_rating": 0.0,
        }

    row = fetch_one(
        """
        SELECT
            COUNT(Review_ID) AS posts_published,
            AVG(Rating) AS avg_rating
        FROM reviews
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
    reviews = fetch_one("SELECT COUNT(*) AS total FROM reviews") if table_exists("reviews") else {}

    return {
        "active_readers": int(readers.get("total") or 0),
        "borrowings_this_month": 0,
        "reviews_published": int(reviews.get("total") or 0),
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
    if not table_exists("reviews"):
        return False, "The reviews table does not exist yet. Run the database setup first."



def get_books_by_title(keyword): 
    query = """
    SELECT
        ISBN,
        Title,
        Author
    FROM books
    WHERE Title LIKE %s
    """
    return fetch_all(query, (f"%{keyword}%",))



def update_book_review_stats(isbn):

    query = """
    UPDATE books b
    SET
        Average_Rating = (
            SELECT ROUND(AVG(r.Rating), 1)
            FROM reviews r
            WHERE r.ISBN = b.ISBN
        ),
        Review_Count = (
            SELECT COUNT(*)
            FROM reviews r
            WHERE r.ISBN = b.ISBN
        )
    WHERE b.ISBN = %s
    """

    execute_query(query, (isbn,))

