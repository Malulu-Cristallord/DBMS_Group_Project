import db_connect


def initiate_books():
    query = (
            "CREATE TABLE IF NOT EXISTS books ("
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
            "User_ID           INT AUTO_INCREMENT PRIMARY KEY,"
            "Name              VARCHAR(100) NOT NULL,"
            "Email             VARCHAR(255) NOT NULL UNIQUE,"
            "Password_Hash     VARCHAR(255) NOT NULL,"
            "Created_At        TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    db_connect.execute_query(query)

def initiate_bookshelf():
    query = ("CREATE TABLE IF NOT EXISTS bookshelf (") #TBA

def initiate_posts():
    query = (
            "CREATE TABLE IF NOT EXISTS posts ("
            "Title            VARCHAR(255),"
            "Post_ID          INT AUTO_INCREMENT PRIMARY KEY NOT NULL,"
            "User_ID          INT REFERENCES Users(User_ID),"
            "Book_ID          INT REFERENCES Books(Book_ID),"
            "Upvote_count     INT,"
            "Created_Date     DATE,"
            "Rating           SMALLINT)"
            )
    db_connect.execute_query(query)

def del_all():
    query = "DROP TABLE IF EXISTS books, users, posts;"
    db_connect.execute_query(query)
    
def execute_all_methods():
    initiate_books()
    initiate_users()
    initiate_posts()


# Run program
print("Welcome to our group project\nBefore we begin, please make sure that you have a database named \'dbms_group_project\" so that the system can connect\n")
print("Select your desired function to run, or enter \'full\' for running all initiate db function:\n"
      "(A) initiate books table\n"
      "(B) initiate users table\n"
      "(C) initiate posts table\n"
      "(N) delete all existing tables (!!Not recommended!!)\n")
dev_input = input()

match dev_input:
    case 'A' :
        initiate_books()
    case 'B' :
        initiate_users()
    case 'C' :
        initiate_posts()
    case 'N' :
        print("THIS IS NO JOKE, DO YOU REALLY WANT TO DELETE THE WHOLE DATABASE???(type \'affirmative\' to confirm)\ntype any key to stop")
        confirmation_input = input()
        if confirmation_input == 'affirmative':
            print("Action confirmed, initiating deletion protocol.")
            del_all()
        else:
            print("Phew, I saved your database")
            exit()
    case "full" :
        execute_all_methods()