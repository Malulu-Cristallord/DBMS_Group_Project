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

def initiate_bookshelf():
    query = ("CREATE TABLE IF NOT EXISTS bookshelf (")

def del_all():
    query = ("DROP TABLE *")
print("Welcome to our group project\nBefore we begin, please make sure that you have a database named \'dbms_group_project\" so that the system can connect\n")
print("Select your desired function to run, or enter \'full\' for running all initiate db function:\n"
      "(A) initiate books table\n"
      "(B) initiate users table\n"
      "(C) initiate bookshelf table\n"
      "(N) delete all existing tables (!!Not recommended!!)\n")
dev_input = input()

initiate_books()
initiate_users()
