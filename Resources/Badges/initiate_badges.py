from Backend.DB_Stuff import db_connect

# name, image path, description, rarity, points
badge_read_01 = ("First Chapter", "Resources/Badges/Badge_Read_01.png", "Read your first book and record it on LibTrack", "common", 10)
badge_read_02 = ("Handful of Knowledge", "Resources/Badges/Badge_Read_02.png", "Read and record 5 reading sessions on LibTrack", "common", 20)
badge_read_03 = ("Open Your Horizons", "Resources/Badges/Badge_Read_03.png", "Read and record 20 reading sessions on LibTrack", "common", 40)
badge_read_04 = ("Your Adventures in Readingland", "Resources/Badges/Badge_Read_04.png", "Read your first book and record it on LibTrack", "uncommon", 100)
badge_read_05 = ("The Reading Games", "Resources/Badges/Badge_Read_05.png", "Read and record 5 reading sessions on LibTrack", "rare", 200)
badge_read_06 = ("The Lord of the Books", "Resources/Badges/Badge_Read_06.png", "Read and record 20 reading sessions on LibTrack", "legendary", 500)
badges_read = (badge_read_01, badge_read_02, badge_read_03, badge_read_04, badge_read_05, badge_read_06)

badge_review_and_post_01 = ("Critic's Pen", "Resources/Badges/Badge_Review&Post_01.png", "Publish your first review on LibTrack", "common", 20)
badge_review_and_post_02 = ("Critic's Diary", "Resources/Badges/Badge_Review&Post_02.png", "Publish your first post on LibTrack", "common", 20)
badges_review_and_post = (badge_review_and_post_01, badge_review_and_post_02)

badge_add_books_01 = ("Knowledge Dripping Like a Faucet", "Resources/Badges/Badge_Add_Books_01.png", "Contribute 10 books to the LibTrack Database", "common", 40)
badge_add_books_02 = ("Knowledge Flowing Like a Shower Head", "Resources/Badges/Badge_Add_Books_02.png", "Contribute 50 books to the LibTrack Database", "uncommon", 100)
badge_add_books_03 = ("Knowledge Flooding Like a Storm", "Resources/Badges/Badge_Add_Books_03.png", "Contribute 200 books to the LibTrack Database", "rare", 200)
badge_add_books_04 = ("Knowledge Invading Like a Sea", "Resources/Badges/Badge_Add_Books_04.png", "Contribute 500 books to the LibTrack Database", "legendary", 400)
badges_add_books = (badge_add_books_01, badge_add_books_02, badge_add_books_03, badge_add_books_04)

all_badges = (badges_read, badges_review_and_post, badges_add_books)

# Waiting for change
def initiate_badges():
    query = """
    INSERT INTO badges(Badge_Name, Badge_Image_Path, Badge_Description, Badge_Rarity, Badge_Points)
    values(%s, %s, %s, %s, %d)
    """
    for badge in all_badges:
        values = (badge[0], badge[1], badge[2], badge[3], badge[4])
        print("values: ", values)
        print("\n")
        db_connect.execute_query(query, values,)

def reader_get_badge(reader_ID: int, badge_id: int):

    if not reader_ID:
        return None

    query1 = """
    SELECT *
    FROM badges
    WHERE Badge_ID = %s
    """

    result = db_connect.execute_query_fetch(query1, (badge_id,))

    if not result:
        print("ERROR: Badge not found")
        return None

    # Add points
    points = result["Badge_Points"]

    query2 = """
    UPDATE readers
    SET Points = Points + %s
    WHERE Reader_ID = %s
    """

    db_connect.execute_query(query2, (points, reader_ID))
    print("points added: ", points)

    # Add to total given badges

    query3 = """
    INSERT INTO given_badges(Given_Badge_ID, Badge_ID, Reader_ID)
    VALUES(%s, %s, %s)
    """
    result = db_connect.execute_query_fetch(query3, (badge_id,))

    return (
        result["Badge_ID"],
        result["Badge_Name"],
        result["Badge_Image_Path"],
        result["Badge_Description"],
        result["Badge_Rarity"],
        result["Badge_Points"],
    )
