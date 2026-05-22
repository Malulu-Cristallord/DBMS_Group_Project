from Backend.DB_Stuff.db_connect import execute_query


def get_saved_books(reader_id):

    query = """
    SELECT b.ISBN, b.Title, b.Author, b.Cover, b.Genre, b.Average_Rating, b.Review_Count, b.Clicked
    FROM books as b
    JOIN Saved_Books as sb on sb.ISBN = b.ISBN
    WHERE sb.reader_ID = %s
    """

    return execute_query(query, (reader_id,))

def save_book(isbn, saved_to_reader_id):
    query = """
    INSERT INTO saved_books(Saved_To_Reader_ID, Saved_Book_ISBN)
    """
    execute_query(query, (isbn, saved_to_reader_id))