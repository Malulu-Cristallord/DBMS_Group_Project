import db_connect


def initiate_books():
    query = ("CREATE TABLE IF NOT EXISTS books ("
             "Title            VARCHAR(255) NOT NULL,"
             "Book_ID          INT AUTO_INCREMENT PRIMARY KEY NOT NULL,"
             "ISBN             VARCHAR(18) NOT NULL,"
             "Category         VARCHAR(255),"
             "Publisher        VARCHAR(255),"
             "Published_Year   YEAR,"
             "Author           VARCHAR(255),"
             "Cover            VARCHAR(255),"
             "Description      VARCHAR(255),"
             "Rating           DECIMAL)")
    db_connect.execute_query(query)


def initiate_users():
    query = (
            "CREATE TABLE IF NOT EXISTS users ("
            "id INT AUTO_INCREMENT PRIMARY KEY,"
            "name VARCHAR(100) NOT NULL,"
            "email VARCHAR(255) NOT NULL UNIQUE,"
            "password_hash VARCHAR(255) NOT NULL,"
            "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    db_connect.execute_query(query)

initiate_books()
initiate_users()