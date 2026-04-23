# db connection
import mysql.connector

db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="your_password",
    database="books_global"
)

if db_connection.is_connected():
    print("Successfully connected to the database")


cursor = db_connection.cursor()
cursor.execute("TRUNCATE TABLE Books")

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

    cursor.execute(query, values)
    db_connection.commit()

    cursor.execute("SELECT * FROM Books")
    rows = cursor.fetchall()

    for row in rows:
        print(row)

test_connection()

cursor.close()
db_connection.close()