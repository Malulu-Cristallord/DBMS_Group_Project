#!/usr/bin/env python3
"""Safe schema check/migration helper for the local LibTrack MySQL database."""
# This script can be used to check for missing tables, columns, and important unique indexes,
# and optionally apply those changes if no data conflicts exist.

from __future__ import annotations

import argparse
import os
import sys
from collections import defaultdict
from pathlib import Path

import mysql.connector


ROOT = Path(__file__).resolve().parents[2]

TABLE_DEFINITIONS = {
    "books": """
        CREATE TABLE IF NOT EXISTS books (
            ISBN             VARCHAR(18)        PRIMARY KEY NOT NULL,
            Title            VARCHAR(255)       NOT NULL,
            Publisher        VARCHAR(255),
            Published_Year   YEAR,
            Author           VARCHAR(255),
            Cover            VARCHAR(255),
            Description      VARCHAR(255),
            Genre            VARCHAR(255),
            Average_Rating   DECIMAL(3, 1)      DEFAULT 0,
            Review_Count     INT                DEFAULT 0,
            Clicked          INT                DEFAULT 0,
            Saved            INT                DEFAULT 0,
            Gathered_At      VARCHAR(255)
        )
    """,
    "readers": """
        CREATE TABLE IF NOT EXISTS readers (
            Reader_ID               INT             AUTO_INCREMENT PRIMARY KEY,
            Name                    VARCHAR(100)    NOT NULL,
            Email                   VARCHAR(255)    NOT NULL UNIQUE,
            Google_Sub              VARCHAR(255)    UNIQUE,
            Password_Hash           VARCHAR(255)    NOT NULL,
            Preferred_Category      VARCHAR(255),
            Points                  INT             DEFAULT 0,
            Books_Read              INT             DEFAULT 0,
            Receive_Recommendations BOOLEAN         DEFAULT TRUE,
            Show_Reading_History    BOOLEAN         DEFAULT TRUE,
            Created_At              TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
            Time_Read               TIME            DEFAULT '00:00:00',
            Daily_Time_Goal         INT             DEFAULT 60,
            Books_Added             INT             DEFAULT 0
        )
    """,
    "posts": """
        CREATE TABLE IF NOT EXISTS posts (
            Post_ID             INT             AUTO_INCREMENT PRIMARY KEY,
            Content             VARCHAR(255),
            Created_Date        TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
            Reader_ID           INT             NOT NULL,
            ISBN                VARCHAR(18),
            CONSTRAINT fk_posts_reader
                FOREIGN KEY (Reader_ID) REFERENCES readers(Reader_ID),
            CONSTRAINT fk_posts_book
                FOREIGN KEY (ISBN) REFERENCES books(ISBN)
        )
    """,
    "reviews": """
        CREATE TABLE IF NOT EXISTS reviews (
            Review_ID           INT             AUTO_INCREMENT PRIMARY KEY,
            Reader_ID           INT,
            ISBN                VARCHAR(18),
            Rating              SMALLINT,
            Content             VARCHAR(255),
            Created_At          TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_reviews_reader
                FOREIGN KEY (Reader_ID) REFERENCES readers(Reader_ID),
            CONSTRAINT fk_reviews_book
                FOREIGN KEY (ISBN) REFERENCES books(ISBN)
        )
    """,
    "recommendations": """
        CREATE TABLE IF NOT EXISTS recommendations (
            Recommendation_ID    INT             AUTO_INCREMENT PRIMARY KEY,
            Reader_ID            INT             NOT NULL,
            ISBN                 VARCHAR(18)     NOT NULL,
            Score                DECIMAL(6, 4)   DEFAULT 0,
            Reason               VARCHAR(255),
            Generated_At         TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
            Status               VARCHAR(50)     DEFAULT 'unread',
            CONSTRAINT fk_recommendations_reader
                FOREIGN KEY (Reader_ID) REFERENCES readers(Reader_ID),
            CONSTRAINT fk_recommendations_book
                FOREIGN KEY (ISBN) REFERENCES books(ISBN),
            CONSTRAINT uq_recommendations_reader_book
                UNIQUE (Reader_ID, ISBN)
        )
    """,
    "likes": """
        CREATE TABLE IF NOT EXISTS likes (
            Like_ID             INT             AUTO_INCREMENT PRIMARY KEY,
            Reader_ID           INT,
            Post_ID             INT,
            CONSTRAINT fk_likes_reader
                FOREIGN KEY (Reader_ID) REFERENCES readers(Reader_ID),
            CONSTRAINT fk_likes_post
                FOREIGN KEY (Post_ID) REFERENCES posts(Post_ID)
        )
    """,
    "comments": """
        CREATE TABLE IF NOT EXISTS comments (
            Comment_ID          INT             AUTO_INCREMENT PRIMARY KEY,
            Reader_ID           INT,
            Post_ID             INT,
            Content             VARCHAR(255),
            Created_At          TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_comments_reader
                FOREIGN KEY (Reader_ID) REFERENCES readers(Reader_ID),
            CONSTRAINT fk_comments_post
                FOREIGN KEY (Post_ID) REFERENCES posts(Post_ID)
        )
    """,
    "badges": """
        CREATE TABLE IF NOT EXISTS badges (
            Badge_ID           INT              AUTO_INCREMENT PRIMARY KEY,
            Badge_Name         VARCHAR(255),
            Badge_Image_Path   VARCHAR(255),
            Badge_Description  TEXT,
            Badge_Rarity       VARCHAR(255),
            Badge_Points       INT
        )
    """,
    "saved_books": """
        CREATE TABLE IF NOT EXISTS saved_books (
            Save_ID              INT AUTO_INCREMENT PRIMARY KEY,
            Saved_Book_ISBN      VARCHAR(18) NOT NULL,
            Saved_To_Reader_ID   INT NOT NULL,
            FOREIGN KEY (Saved_Book_ISBN)
                REFERENCES books(ISBN)
                ON DELETE CASCADE,
            FOREIGN KEY (Saved_To_Reader_ID)
                REFERENCES readers(Reader_ID)
                ON DELETE CASCADE,
            UNIQUE KEY unique_saved_book (
                Saved_Book_ISBN,
                Saved_To_Reader_ID
            )
        )
    """,
    "given_badges": """
        CREATE TABLE IF NOT EXISTS given_badges (
            Given_Badge_ID       INT AUTO_INCREMENT PRIMARY KEY,
            Badge_ID             INT NOT NULL,
            Reader_ID            INT NOT NULL,
            Given_Time           DATETIME DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_given_badge_id
                FOREIGN KEY (Badge_ID) REFERENCES badges(Badge_ID),
            CONSTRAINT fk_given_to_reader_id
                FOREIGN KEY (Reader_ID) REFERENCES readers(Reader_ID)
        )
    """,
}

COLUMN_DEFINITIONS = {
    "books": {
        "Title": "Title VARCHAR(255) NULL",
        "Publisher": "Publisher VARCHAR(255)",
        "Published_Year": "Published_Year YEAR",
        "Author": "Author VARCHAR(255)",
        "Cover": "Cover VARCHAR(255)",
        "Description": "Description VARCHAR(255)",
        "Genre": "Genre VARCHAR(255)",
        "Average_Rating": "Average_Rating DECIMAL(3, 1) DEFAULT 0",
        "Review_Count": "Review_Count INT DEFAULT 0",
        "Clicked": "Clicked INT DEFAULT 0",
        "Saved": "Saved INT DEFAULT 0",
        "Gathered_At": "Gathered_At VARCHAR(255)",
    },
    "readers": {
        "Name": "Name VARCHAR(100) NULL",
        "Email": "Email VARCHAR(255) NULL",
        "Google_Sub": "Google_Sub VARCHAR(255) NULL",
        "Password_Hash": "Password_Hash VARCHAR(255) NULL",
        "Preferred_Category": "Preferred_Category VARCHAR(255)",
        "Points": "Points INT DEFAULT 0",
        "Books_Read": "Books_Read INT DEFAULT 0",
        "Receive_Recommendations": "Receive_Recommendations BOOLEAN DEFAULT TRUE",
        "Show_Reading_History": "Show_Reading_History BOOLEAN DEFAULT TRUE",
        "Created_At": "Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        "Time_Read": "Time_Read TIME DEFAULT '00:00:00'",
        "Daily_Time_Goal": "Daily_Time_Goal INT DEFAULT 60",
        "Books_Added": "Books_Added INT DEFAULT 0",
    },
    "posts": {
        "Content": "Content VARCHAR(255)",
        "Created_Date": "Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        "Reader_ID": "Reader_ID INT",
        "ISBN": "ISBN VARCHAR(18)",
    },
    "reviews": {
        "Reader_ID": "Reader_ID INT",
        "ISBN": "ISBN VARCHAR(18)",
        "Rating": "Rating SMALLINT",
        "Content": "Content VARCHAR(255)",
        "Created_At": "Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    },
    "recommendations": {
        "Reader_ID": "Reader_ID INT",
        "ISBN": "ISBN VARCHAR(18)",
        "Score": "Score DECIMAL(6, 4) DEFAULT 0",
        "Reason": "Reason VARCHAR(255)",
        "Generated_At": "Generated_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        "Status": "Status VARCHAR(50) DEFAULT 'unread'",
    },
    "likes": {
        "Reader_ID": "Reader_ID INT",
        "Post_ID": "Post_ID INT",
    },
    "comments": {
        "Reader_ID": "Reader_ID INT",
        "Post_ID": "Post_ID INT",
        "Content": "Content VARCHAR(255)",
        "Created_At": "Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    },
    "badges": {
        "Badge_Name": "Badge_Name VARCHAR(255)",
        "Badge_Image_Path": "Badge_Image_Path VARCHAR(255)",
        "Badge_Description": "Badge_Description TEXT",
        "Badge_Rarity": "Badge_Rarity VARCHAR(255)",
        "Badge_Points": "Badge_Points INT",
    },
    "saved_books": {
        "Saved_Book_ISBN": "Saved_Book_ISBN VARCHAR(18)",
        "Saved_To_Reader_ID": "Saved_To_Reader_ID INT",
    },
    "given_badges": {
        "Badge_ID": "Badge_ID INT",
        "Reader_ID": "Reader_ID INT",
        "Given_Time": "Given_Time DATETIME DEFAULT CURRENT_TIMESTAMP",
    },
}

SAFE_UNIQUE_INDEXES = {
    "readers": [
        ("Email",),
        ("Google_Sub",),
    ],
    "saved_books": [
        ("Saved_Book_ISBN", "Saved_To_Reader_ID"),
    ],
    "recommendations": [
        ("Reader_ID", "ISBN"),
    ],
}

RECOMMENDED_UNIQUE_INDEXES = {
    "reviews": [
        ("Reader_ID", "ISBN"),
    ],
    "likes": [
        ("Post_ID", "Reader_ID"),
    ],
    "given_badges": [
        ("Reader_ID", "Badge_ID"),
    ],
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


def quote_identifier(identifier: str) -> str:
    return f"`{identifier.replace('`', '``')}`"


def fetch_all(cursor, query: str, params: tuple = ()) -> list[dict]:
    cursor.execute(query, params)
    return cursor.fetchall()


def get_tables(cursor) -> set[str]:
    rows = fetch_all(
        cursor,
        """
        SELECT table_name AS table_name
        FROM information_schema.tables
        WHERE table_schema = DATABASE()
          AND table_type = 'BASE TABLE'
        """,
    )
    return {row["table_name"] for row in rows}


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


def has_column(existing_columns: set[str], column_name: str) -> bool:
    return column_name.lower() in {column.lower() for column in existing_columns}


def unique_exists(indexes: list[tuple[str, ...]], columns: tuple[str, ...]) -> bool:
    expected = tuple(column.lower() for column in columns)
    return any(tuple(column.lower() for column in index) == expected for index in indexes)


def has_duplicate_rows(cursor, table: str, columns: tuple[str, ...]) -> bool:
    quoted_columns = ", ".join(quote_identifier(column) for column in columns)
    not_null = " AND ".join(f"{quote_identifier(column)} IS NOT NULL" for column in columns)
    query = f"""
        SELECT {quoted_columns}, COUNT(*) AS total
        FROM {quote_identifier(table)}
        WHERE {not_null}
        GROUP BY {quoted_columns}
        HAVING COUNT(*) > 1
        LIMIT 1
    """
    rows = fetch_all(cursor, query)
    return bool(rows)


def add_unique_index(cursor, table: str, columns: tuple[str, ...]) -> None:
    index_name = "uq_" + table + "_" + "_".join(columns)
    cursor.execute(
        f"""
        ALTER TABLE {quote_identifier(table)}
        ADD UNIQUE KEY {quote_identifier(index_name)}
        ({', '.join(quote_identifier(column) for column in columns)})
        """
    )


def migrate_tables(cursor, apply: bool) -> bool:
    changed = False
    existing_tables = get_tables(cursor)

    for table, create_sql in TABLE_DEFINITIONS.items():
        if table in existing_tables:
            print(f"[OK] Table exists: {table}")
            continue

        changed = True
        if apply:
            cursor.execute(create_sql)
            print(f"[APPLY] Created missing table: {table}")
        else:
            print(f"[DRY-RUN] Would create missing table: {table}")

    return changed


def migrate_columns(cursor, apply: bool) -> bool:
    changed = False
    columns_by_table = get_columns(cursor)

    for table, column_defs in COLUMN_DEFINITIONS.items():
        existing_columns = columns_by_table.get(table, set())
        if not existing_columns:
            continue

        for column_name, column_definition in column_defs.items():
            if has_column(existing_columns, column_name):
                continue

            changed = True
            sql = f"ALTER TABLE {quote_identifier(table)} ADD COLUMN {column_definition}"
            if apply:
                cursor.execute(sql)
                print(f"[APPLY] Added {table}.{column_name}")
            else:
                print(f"[DRY-RUN] Would add {table}.{column_name}: {column_definition}")

    return changed


def migrate_unique_indexes(
    cursor,
    apply: bool,
    include_recommended_uniques: bool,
) -> bool:
    changed = False
    columns_by_table = get_columns(cursor)
    unique_indexes = get_unique_indexes(cursor)
    groups = dict(SAFE_UNIQUE_INDEXES)

    if include_recommended_uniques:
        groups.update(RECOMMENDED_UNIQUE_INDEXES)

    for table, index_columns_list in groups.items():
        existing_columns = columns_by_table.get(table, set())
        if not existing_columns:
            continue

        for index_columns in index_columns_list:
            if any(not has_column(existing_columns, column) for column in index_columns):
                print(f"[WARN] Cannot add unique {table}{index_columns}; missing column")
                continue

            if unique_exists(unique_indexes.get(table, []), index_columns):
                continue

            if has_duplicate_rows(cursor, table, index_columns):
                print(f"[WARN] Cannot add unique {table}{index_columns}; duplicate rows exist")
                continue

            changed = True
            if apply:
                add_unique_index(cursor, table, index_columns)
                print(f"[APPLY] Added unique index on {table}{index_columns}")
            else:
                print(f"[DRY-RUN] Would add unique index on {table}{index_columns}")

    if not include_recommended_uniques:
        for table, index_columns_list in RECOMMENDED_UNIQUE_INDEXES.items():
            for index_columns in index_columns_list:
                print(
                    f"[INFO] Recommended unique not auto-applied: {table}{index_columns}. "
                    "Use --with-recommended-uniques after checking duplicates."
                )

    return changed


def warn_sensitive_gaps(cursor) -> None:
    columns_by_table = get_columns(cursor)
    reader_columns = columns_by_table.get("readers", set())

    if has_column(reader_columns, "Password_Hash"):
        rows = fetch_all(
            cursor,
            """
            SELECT Reader_ID, Email
            FROM readers
            WHERE Password_Hash IS NULL
               OR Password_Hash NOT LIKE '$2%'
            LIMIT 10
            """,
        )
        if rows:
            print(
                "[WARN] Some readers do not have bcrypt Password_Hash values. "
                "Those accounts need password reset or re-registration."
            )
            for row in rows:
                print(f"       Reader_ID={row.get('Reader_ID')} Email={row.get('Email')}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check or safely migrate the local LibTrack MySQL schema."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply safe schema changes. Without this flag, only prints a dry-run.",
    )
    parser.add_argument(
        "--with-recommended-uniques",
        action="store_true",
        help=(
            "Also add recommended duplicate-prevention unique indexes for reviews, "
            "likes, and given_badges when no duplicates exist."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        connection = connect()
    except Exception as exc:
        print(f"[FAIL] Could not connect to MySQL: {exc}")
        print("Start MySQL and check .env DB_HOST/DB_PORT/DB_USER/DB_PASSWORD/DB_NAME.")
        return 2

    try:
        cursor = connection.cursor(dictionary=True)
        print("Mode:", "APPLY" if args.apply else "DRY-RUN")
        changed = False
        changed |= migrate_tables(cursor, args.apply)
        changed |= migrate_columns(cursor, args.apply)
        changed |= migrate_unique_indexes(cursor, args.apply, args.with_recommended_uniques)
        warn_sensitive_gaps(cursor)

        if args.apply:
            connection.commit()
            print("Migration committed.")
        else:
            print("Dry-run complete. Re-run with --apply to make these changes.")

        if not changed:
            print("No schema changes needed.")

        return 0
    except Exception as exc:
        if args.apply:
            connection.rollback()
        print(f"[FAIL] Migration failed: {exc}")
        return 1
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        connection.close()


if __name__ == "__main__":
    sys.exit(main())
