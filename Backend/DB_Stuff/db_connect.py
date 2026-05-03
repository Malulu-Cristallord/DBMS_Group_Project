# db connection
import mysql.connector
import os

def test_env():
    print(os.getenv('DB_PASSWORD'))


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv('DB_PASSWORD'),
        database="dbms_group_project",
        connection_timeout=5
    )

def execute_query(query):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        print("committed")

    except mysql.connector.Error as e:
        return f"DB Error: {str(e)}"

    finally:
        cursor.close()
        conn.close()

def insert_book(query, values=None):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        if values:
            cursor.execute(query, values)
        else:
            cursor.execute(query)

        conn.commit()

    except mysql.connector.Error as e:
        return f"DB Error: {str(e)}"

    finally:
        cursor.close()
        conn.close()

    print("Insert successful")
    return None


def test_connection():
    query = """
    INSERT INTO Books
    (Title, Book_ID, ISBN, Category, Author, Rating, Description, Publisher, Published_Year)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        'Harry Potter and the Deathly Hallows',
        1,
        '9780747595823',
        'Fantasy',
        'J.K. Rowling',
        None,
        None,
        'Bloomsbury',
        2008
    )

    insert_book(query, values)


def clean_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("TRUNCATE Books")
    conn.commit()
    cursor.close()
    conn.close()

test_env()
test_connection()
clean_table()