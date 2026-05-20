from Backend.DB_Stuff.db_connect import execute_query


def get_saved_books(reader):

    query = """
    SELECT books
    """

    execute_query(query, ())
