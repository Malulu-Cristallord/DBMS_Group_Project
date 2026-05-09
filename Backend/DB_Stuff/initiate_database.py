#from Backend.DB_Stuff 
import db_connect


def initiate_books():
    query = """
    CREATE TABLE IF NOT EXISTS books (
        ISBN             VARCHAR(18)        PRIMARY KEY NOT NULL,
        Title            VARCHAR(255)       NOT NULL,
        Publisher        VARCHAR(255),
        Published_Year   YEAR,
        Author           VARCHAR(255),
        Cover            VARCHAR(255),
        Description      VARCHAR(255),
        Rating           DECIMAL(3, 1)      DEFAULT 0,
        Average_Rating   DECIMAL(3, 1)      DEFAULT 0,
        Clicked          INT                DEFAULT 0,
        Saved            INT                DEFAULT 0
    )
    """
    db_connect.execute_query(query)
def initiate_book_categories():
    query = """
    CREATE TABLE IF NOT EXISTS book_categories (
        Category_ID      INT AUTO_INCREMENT PRIMARY KEY,
        ISBN             VARCHAR(18) REFERENCES Books(ISBN),
        Category         VARCHAR(255)
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
        Content             VARCHAR(255),
        Created_Date        TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
        Reader_ID           INT             NOT NULL,
        ISBN                VARCHAR(18),
        CONSTRAINT fk_posts_reader
            FOREIGN KEY (Reader_ID) REFERENCES readers(Reader_ID),
        CONSTRAINT fk_posts_book
            FOREIGN KEY (ISBN) REFERENCES books(ISBN)
    )
    """
    db_connect.execute_query(query)


def initiate_reviews():
    query = """
    CREATE TABLE IF NOT EXISTS reviews (
        Review_ID           INT             AUTO_INCREMENT PRIMARY KEY,
        Reader_ID           INT,
        ISBN                VARCHAR(18),
        Rating              SMALLINT,
        Content             VARCHAR(255),
        Created_At          TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT fk_reviews_reader
            FOREIGN KEY (Reader_ID) REFERENCES readers(Reader_ID),
        CONSTRAINT fk_reviews_book
            FOREIGN KEY (ISBN) REFERENCES books(ISBN)
    )
    """
    db_connect.execute_query(query)


def initiate_recommendations():
    query = """
    CREATE TABLE IF NOT EXISTS recommendations (
        Recommendation_ID    INT             AUTO_INCREMENT PRIMARY KEY,
        Reader_ID            INT             NOT NULL,
        ISBN                 VARCHAR(18)     NOT NULL,
        Score                DECIMAL(6, 4)   DEFAULT 0,
        Reason               VARCHAR(255),
        Generated_At         TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
        Status               VARCHAR(50)     DEFAULT 'unread',
        CONSTRAINT fk_recommendations_reader
            FOREIGN KEY (Reader_ID) REFERENCES readers(Reader_ID),
        CONSTRAINT fk_recommendations_book
            FOREIGN KEY (ISBN) REFERENCES books(ISBN),
        CONSTRAINT uq_recommendations_reader_book
            UNIQUE (Reader_ID, ISBN)
    )
    """
    db_connect.execute_query(query)


def initiate_likes():
    query = """
    CREATE TABLE IF NOT EXISTS likes (
        Like_ID             INT             AUTO_INCREMENT PRIMARY KEY,
        Reader_ID           INT,
        Post_ID             INT,
        CONSTRAINT fk_likes_reader
            FOREIGN KEY (Reader_ID) REFERENCES readers(Reader_ID),
        CONSTRAINT fk_likes_post
            FOREIGN KEY (Post_ID) REFERENCES posts(Post_ID)
    )
    """
    db_connect.execute_query(query)



def initiate_comments():
    query = """
    CREATE TABLE IF NOT EXISTS comments (
        Comment_ID          INT             AUTO_INCREMENT PRIMARY KEY,
        Reader_ID           INT,
        Post_ID             INT,
        Content             VARCHAR(255),
        Created_At          TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT fk_comments_reader
            FOREIGN KEY (Reader_ID) REFERENCES readers(Reader_ID),
        CONSTRAINT fk_comments_post
            FOREIGN KEY (Post_ID) REFERENCES posts(Post_ID)
    )
    """
    db_connect.execute_query(query)


def initiate_rewards():
    query = """
    CREATE TABLE IF NOT EXISTS rewards (
        Reward_ID           INT             AUTO_INCREMENT PRIMARY KEY,
        Reward_Name         VARCHAR(255),
        Description         VARCHAR(255),
        Reward_Type         VARCHAR(100),
        Points_Required     INT             DEFAULT 0
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
    query = """
    DROP TABLE IF EXISTS
        recommendations,
        comments,
        likes,
        reviews,
        posts,
        rewards,
        badges,
        books,
        readers
    """
    db_connect.execute_query(query)


def execute_all_methods():
    initiate_books()
    initiate_readers()
    initiate_posts()
    initiate_reviews()
    initiate_recommendations()
    initiate_likes()
    initiate_comments()
    initiate_rewards()
    initiate_badges()
    initiate_book_categories()

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
    "(Aa)initiate books category table\n"
    "(B) initiate readers table\n"
    "(C) initiate posts table\n"
    "(D) initiate rewards/badges table\n"
    "(R) initiate recommendations table\n"
    "(N) delete all existing tables\n\n"
    "(full) initiate all tables\n\n"
    "(z) test"
)
dev_input = input()

match dev_input:
    case "A":
        initiate_books()
    case "Aa":
        initiate_book_categories()
    case "B":
        initiate_readers()
    case "C":
        initiate_posts()
    case "D":
        initiate_rewards()
        initiate_badges()
    case "R":
        initiate_recommendations()
    case "N":
        confirmation_input = input("THIS IS NO JOKE! TYPE \'affirmative\' TO CONFIRM DELETION").strip()
        if confirmation_input == "affirmative":
            del_all()
    case "full":
        execute_all_methods()
    case "z":
        data_test()
