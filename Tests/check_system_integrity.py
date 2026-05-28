#!/usr/bin/env python3
"""Read-only ERD/system integrity checks for the LibTrack database."""
# This script connects to the MySQL database and performs checks to verify that:
# 1. All expected tables and columns from the ERD are present (with some flexibility in naming).
# 2. Recommended unique constraints are in place to prevent common data issues.
# 3. Basic data consistency checks, such as no duplicate saved books or likes, and that review aggregates match the underlying reviews.

from __future__ import annotations

import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable

import mysql.connector


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_COLUMNS = {
    "readers": {
        "reader_id": ["Reader_ID", "reader_id"],
        "name": ["Name", "name"],
        "email": ["Email", "email"],
        "password_hash": ["Password_Hash", "password_hash"],
        "Google_sub": ["Google_Sub", "Google_sub"],
        "preferred_category": ["Preferred_Category", "preferred_category"],
        "books_read": ["Books_Read", "books_read"],
        "receive_recommendations": ["Receive_Recommendations", "receive_recommendations"],
        "show_reading_history": ["Show_Reading_History", "show_reading_history"],
        "point": ["Point", "Points", "point", "points"],
        "daily_time_goal": ["Daily_Time_Goal", "daily_time_goal"],
        "create_at": ["Create_At", "Created_At", "create_at", "created_at"],
    },
    "books": {
        "ISBN": ["ISBN"],
        "title": ["Title", "title"],
        "author": ["Author", "author"],
        "Publisher": ["Publisher", "publisher"],
        "Publish_year": ["Publish_Year", "Published_Year", "publish_year", "published_year"],
        "cover": ["Cover", "cover"],
        "description": ["Description", "description"],
        "genre": ["Genre", "genre"],
        "saved": ["Saved", "saved"],
        "gathered_at": ["Gathered_At", "gathered_at"],
        "average_rating": ["Average_Rating", "average_rating"],
        "review_count": ["Review_Count", "review_count"],
        "clicked": ["Clicked", "clicked"],
    },
    "saved_books": {
        "save_id": ["Save_ID", "save_id"],
        "save_book_isbn": ["Saved_Book_ISBN", "Save_Book_ISBN", "save_book_isbn"],
        "save_to_reader_id": ["Saved_To_Reader_ID", "Save_To_Reader_ID", "save_to_reader_id"],
    },
    "recommendations": {
        "recommendation_id": ["Recommendation_ID", "recommendation_id"],
        "reader_id": ["Reader_ID", "reader_id"],
        "ISBN": ["ISBN"],
        "score": ["Score", "score"],
        "generated_at": ["Generated_At", "generated_at"],
        "reason": ["Reason", "reason"],
        "status": ["Status", "status"],
    },
    "reviews": {
        "review_id": ["Review_ID", "review_id"],
        "reader_id": ["Reader_ID", "reader_id"],
        "ISBN": ["ISBN"],
        "content": ["Content", "content"],
        "rating": ["Rating", "rating"],
        "create_at": ["Create_At", "Created_At", "create_at", "created_at"],
    },
    "posts": {
        "post_id": ["Post_ID", "post_id"],
        "reader_id": ["Reader_ID", "reader_id"],
        "ISBN": ["ISBN"],
        "content": ["Content", "content"],
        "created_date": ["Created_Date", "created_date"],
    },
    "likes": {
        "like_id": ["Like_ID", "like_id"],
        "post_id": ["Post_ID", "post_id"],
        "reader_id": ["Reader_ID", "reader_id"],
    },
    "comments": {
        "comment_id": ["Comment_ID", "comment_id"],
        "post_id": ["Post_ID", "post_id"],
        "reader_id": ["Reader_ID", "reader_id"],
        "content": ["Content", "content"],
        "create_at": ["Create_At", "Created_At", "create_at", "created_at"],
    },
    "badges": {
        "badge_id": ["Badge_ID", "badge_id"],
        "badge_name": ["Badge_Name", "badge_name"],
        "badge_description": ["Badge_Description", "badge_description"],
        "badge_image_path": ["Badge_Image_Path", "badge_image_path"],
        "badge_rarity": ["Badge_Rarity", "badge_rarity"],
        "badge_points": ["Badge_Points", "badge_points"],
    },
    "given_badges": {
        "given_badges_id": ["Given_Badges_ID", "Given_Badge_ID", "given_badges_id"],
        "reader_id": ["Reader_ID", "reader_id"],
        "badge_id": ["Badge_ID", "badge_id"],
    },
}

RECOMMENDED_UNIQUES = {
    "readers": ("Email",),
    "saved_books": ("Saved_Book_ISBN", "Saved_To_Reader_ID"),
    "recommendations": ("Reader_ID", "ISBN"),
    "reviews": ("Reader_ID", "ISBN"),
    "likes": ("Post_ID", "Reader_ID"),
    "given_badges": ("Reader_ID", "Badge_ID"),
}


def load_dotenv() -> None:
    dotenv = ROOT / ".env"
    if not dotenv.exists():
        return

    for raw_line in dotenv.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def connect():
    load_dotenv()
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "dbms_group_project"),
        connection_timeout=5,
    )


def fetch_all(cursor, query: str, params: tuple = ()) -> list[dict]:
    cursor.execute(query, params)
    return cursor.fetchall()


def get_columns(cursor) -> dict[str, set[str]]:
    rows = fetch_all(
        cursor,
        """
        SELECT
            table_name AS table_name,
            column_name AS column_name
        FROM information_schema.columns
        WHERE table_schema = DATABASE()
        """,
    )
    columns: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        columns[row["table_name"]].add(row["column_name"])
    return columns


def get_unique_indexes(cursor) -> dict[str, list[tuple[str, ...]]]:
    rows = fetch_all(
        cursor,
        """
        SELECT
            table_name AS table_name,
            index_name AS index_name,
            seq_in_index AS seq_in_index,
            column_name AS column_name
        FROM information_schema.statistics
        WHERE table_schema = DATABASE()
          AND non_unique = 0
        ORDER BY table_name, index_name, seq_in_index
        """,
    )
    grouped: dict[tuple[str, str], list[tuple[int, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row["table_name"], row["index_name"])].append(
            (int(row["seq_in_index"]), row["column_name"])
        )

    indexes: dict[str, list[tuple[str, ...]]] = defaultdict(list)
    for (table, _index_name), values in grouped.items():
        indexes[table].append(tuple(column for _, column in sorted(values)))
    return indexes


def find_column(actual_columns: set[str], aliases: Iterable[str]) -> str | None:
    lower_lookup = {column.lower(): column for column in actual_columns}
    for alias in aliases:
        if alias in actual_columns:
            return alias
        if alias.lower() in lower_lookup:
            return lower_lookup[alias.lower()]
    return None


def check_schema(cursor) -> int:
    failures = 0
    columns_by_table = get_columns(cursor)
    unique_indexes = get_unique_indexes(cursor)

    print("== ERD column compatibility ==")
    for table, expected in EXPECTED_COLUMNS.items():
        actual_columns = columns_by_table.get(table, set())
        if not actual_columns:
            print(f"[FAIL] Missing table: {table}")
            failures += 1
            continue

        for erd_name, aliases in expected.items():
            actual = find_column(actual_columns, aliases)
            if not actual:
                print(f"[FAIL] {table}.{erd_name} missing. Compatible names: {aliases}")
                failures += 1
            elif actual == erd_name:
                print(f"[OK] {table}.{erd_name}")
            else:
                print(f"[OK-COMPAT] {table}.{erd_name} stored as {actual}")

    print("\n== Recommended uniqueness constraints ==")
    for table, expected_columns in RECOMMENDED_UNIQUES.items():
        indexes = unique_indexes.get(table, [])
        if expected_columns in indexes:
            print(f"[OK] {table} unique {expected_columns}")
        else:
            print(f"[WARN] {table} should consider unique {expected_columns}")

    return failures


def check_data(cursor) -> None:
    print("\n== Data consistency checks ==")
    checks = [
        (
            "duplicate saved books",
            """
            SELECT Saved_Book_ISBN, Saved_To_Reader_ID, COUNT(*) AS total
            FROM saved_books
            GROUP BY Saved_Book_ISBN, Saved_To_Reader_ID
            HAVING COUNT(*) > 1
            """,
        ),
        (
            "duplicate likes",
            """
            SELECT Post_ID, Reader_ID, COUNT(*) AS total
            FROM likes
            GROUP BY Post_ID, Reader_ID
            HAVING COUNT(*) > 1
            """,
        ),
        (
            "duplicate given badges",
            """
            SELECT Reader_ID, Badge_ID, COUNT(*) AS total
            FROM given_badges
            GROUP BY Reader_ID, Badge_ID
            HAVING COUNT(*) > 1
            """,
        ),
        (
            "duplicate reader reviews for one book",
            """
            SELECT Reader_ID, ISBN, COUNT(*) AS total
            FROM reviews
            GROUP BY Reader_ID, ISBN
            HAVING COUNT(*) > 1
            """,
        ),
        (
            "non-bcrypt reader password hashes",
            """
            SELECT Reader_ID, Email
            FROM readers
            WHERE Password_Hash IS NULL
               OR Password_Hash NOT LIKE '$2%'
            LIMIT 20
            """,
        ),
        (
            "review aggregate mismatches",
            """
            SELECT b.ISBN, b.Average_Rating, b.Review_Count,
                   ROUND(AVG(r.Rating), 1) AS expected_average,
                   COUNT(r.Review_ID) AS expected_count
            FROM books b
            LEFT JOIN reviews r ON r.ISBN = b.ISBN
            GROUP BY b.ISBN, b.Average_Rating, b.Review_Count
            HAVING COALESCE(b.Review_Count, 0) <> COUNT(r.Review_ID)
                OR COALESCE(b.Average_Rating, 0) <> COALESCE(ROUND(AVG(r.Rating), 1), 0)
            LIMIT 20
            """,
        ),
    ]

    for label, query in checks:
        try:
            rows = fetch_all(cursor, query)
        except mysql.connector.Error as exc:
            print(f"[WARN] Could not run {label}: {exc}")
            continue

        if rows:
            print(f"[WARN] {label}: {len(rows)} row(s) need review")
            for row in rows[:5]:
                print(f"       {row}")
        else:
            print(f"[OK] {label}")


def main() -> int:
    try:
        connection = connect()
    except Exception as exc:
        print(f"[FAIL] Could not connect to MySQL: {exc}")
        print("Start MySQL, set DB_PASSWORD or .env, and initialize dbms_group_project first.")
        return 2

    try:
        cursor = connection.cursor(dictionary=True)
        failures = check_schema(cursor)
        check_data(cursor)
        return 1 if failures else 0
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        connection.close()


if __name__ == "__main__":
    sys.exit(main())
