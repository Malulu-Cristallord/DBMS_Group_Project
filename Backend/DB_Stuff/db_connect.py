import os

import mysql.connector


def test_env():
    print(os.getenv("DB_PASSWORD"))


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "dbms_group_project"),
        connection_timeout=5,
    )


def execute_query(query, values=None):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(query, values or ())
        connection.commit()
        return None
    except mysql.connector.Error as exc:
        if connection:
            connection.rollback()
        return f"DB Error: {exc}"
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def insert_book(query, values=None):
    error = execute_query(query, values)
    if error:
        return error
    return None


def test_connection():
    query = """
    INSERT INTO books
    (Title, ISBN, Category, Author, Rating, Description, Publisher, Published_Year)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        "Harry Potter and the Deathly Hallows",
        "9780747595823",
        "Fantasy",
        "J.K. Rowling",
        None,
        None,
        "Bloomsbury",
        2008,
    )

    return insert_book(query, values)

def clean_table():
    return execute_query("TRUNCATE TABLE books")
