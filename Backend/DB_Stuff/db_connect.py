import os

import mysql.connector



def test_env():
    print(os.getenv("DB_PASSWORD"))


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD"),
        database="dbms_group_project",
        connection_timeout=5,
        # From Malu: Do not change this function
    )


def execute_query(query, values=None):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(query, values or ())
        connection.commit()
        print("Query committed")
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
    CREATE TABLE IF NOT EXISTS books (
        Book_ID          INT                AUTO_INCREMENT PRIMARY KEY,
        Title            VARCHAR(255)       NOT NULL,
        ISBN             VARCHAR(18)        NOT NULL,
        Category         VARCHAR(255),
        Publisher        VARCHAR(255),
        Published_Year   YEAR,
        Author           VARCHAR(255),
        Cover            VARCHAR(255),
        Description      VARCHAR(255),
        Rating           DECIMAL(3, 1)
    )
    """
    execute_query(query)

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
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("TRUNCATE Books")
    conn.commit()
    cursor.close()
    conn.close()

test_env()
print(get_connection())