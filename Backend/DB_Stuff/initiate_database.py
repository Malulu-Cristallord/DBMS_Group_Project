#from Backend.DB_Stuff 
import db_connect


def initiate_books():
    query = """
    CREATE TABLE IF NOT EXISTS books (
        Title            VARCHAR(255)       PRIMARY KEY NOT NULL,
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
    db_connect.execute_query(query)


def initiate_readers():
    query = """
    CREATE TABLE IF NOT EXISTS readers (
        Reader_ID               INT             AUTO_INCREMENT PRIMARY KEY,
        Name                    VARCHAR(100)    NOT NULL,
        Email                   VARCHAR(255)    NOT NULL UNIQUE,
        Password_Hash           VARCHAR(255)    NOT NULL,
        Preferred_Category      VARCHAR(255),
        Points                  INT             DEFAULT 0,
        Books_Read              INT             DEFAULT 0,
        Receive_Recommendations BOOLEAN         DEFAULT TRUE,
        Show_Reading_History    BOOLEAN         DEFAULT TRUE,
        Created_At              TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
    )
    """
    db_connect.execute_query(query)


def initiate_posts():
    query = """
    CREATE TABLE IF NOT EXISTS posts (
        Post_ID             INT             AUTO_INCREMENT PRIMARY KEY,
        Title               VARCHAR(255),
        Reader_ID           INT,
        ISBN                VARCHAR(18) REFERENCES books(ISBN),
        Upvote_Count        INT DEFAULT 0,
        Created_Date        DATE,
        Rating              SMALLINT,
        CONSTRAINT fk_posts_reader
            FOREIGN KEY (Reader_ID) REFERENCES readers(Reader_ID)
    )
    """
    db_connect.execute_query(query)

def initiate_badges():
    query = """
    CREATE TABLE IF NOT EXISTS badges (
    Badge_ID           INT              PRIMARY KEY,
    Badge_Name         VARCHAR(255),
    Badge_Image_Path   VARCHAR(255),
    Badge_Description  VARCHAR(255), 
    Badge_Points       INT)
    """
    db_connect.execute_query(query)

def del_all():
    query = "DROP TABLE IF EXISTS posts, books, readers"
    db_connect.execute_query(query)


def execute_all_methods():
    initiate_books()
    initiate_readers()
    initiate_posts()

def data_test():
    query = "CREATE TABLE IF NOT EXISTS test(test int)"
    db_connect.execute_query(query)
    query = "INSERT INTO test (test) VALUES (1)"
    db_connect.execute_query(query)
    query = "SELECT * FROM test"
    db_connect.execute_query(query)


print(
    "Welcome to LibTrack database setup. Make sure database "
    "'dbms_group_project' exists before running this script."
)
print(
    "Select a setup option:\n"
    "(A) initiate books table\n"
    "(B) initiate readers table\n"
    "(C) initiate posts table\n"
    "(D) initiate badges table\n"
    "(N) delete all existing tables\n\n"
    "(full) initiate all tables\n\n"
    "(z) test"
)
dev_input = input()

match dev_input:
    case "A":
        initiate_books()
    case "B":
        initiate_readers()
    case "C":
        initiate_posts()
    case "D":
        initiate_badges()
    case "N":
        confirmation_input = input("THIS IS NO JOKE! TYPE \'affirmative\' TO CONFIRM DELETION").strip()
        if confirmation_input == "affirmative":
            del_all()
    case "full":
        execute_all_methods()
    case "z":
        data_test()
