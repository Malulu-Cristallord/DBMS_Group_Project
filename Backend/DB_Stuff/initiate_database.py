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


def initiate_readers():
    query = (
        """
        CREATE TABLE IF NOT EXISTS readers (
        reader_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(255) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        preferred_category VARCHAR(255),
        points INT DEFAULT 0,
        receive_recommendations BOOLEAN DEFAULT TRUE,
        show_reading_history BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
        """
    )
    db_connect.execute_query(query)

def initiate_bookshelf():
    query = ("CREATE TABLE IF NOT EXISTS bookshelf (") #TBA

def initiate_posts():
    query = (
            "CREATE TABLE IF NOT EXISTS posts ("
            "Title            VARCHAR(255),"
            "Post_ID          INT AUTO_INCREMENT PRIMARY KEY NOT NULL,"
            "Reader_ID          INT REFERENCES Readers(Reader_ID),"
            "Book_ID          INT REFERENCES Books(Book_ID),"
            "Upvote_count     INT,"
            "Created_Date     DATE,"
            "Rating           SMALLINT)"
            )
    db_connect.execute_query(query)

def del_all():
    query = "DROP TABLE IF EXISTS books, readers, posts;"
    db_connect.execute_query(query)
    
def execute_all_methods():
    initiate_books()
    initiate_readers()
    initiate_posts()


# Run program
print("Welcome to our group project\nBefore we begin, please make sure that you have a database named \'dbms_group_project\" so that the system can connect\n")
print("Select your desired function to run, or enter \'full\' for running all initiate db function:\n"
      "(A) initiate books table\n"
      "(B) initiate readers table\n"
      "(C) initiate posts table\n"
      "(N) delete all existing tables (!!Not recommended!!)\n")
dev_input = input()

match dev_input:
    case 'A' :
        initiate_books()
    case 'B' :
        initiate_readers()
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