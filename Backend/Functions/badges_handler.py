from Backend.DB_Stuff import db_connect


def reader_get_badge(reader_ID: int, badge_id: int):

    if not reader_ID:
        return None

    # Check if badge already owned
    check_query = """
    SELECT *
    FROM given_badges
    WHERE Badge_ID = %s
    AND Reader_ID = %s
    """

    existing = db_connect.execute_query_fetch(
        check_query,
        (badge_id, reader_ID)
    )

    if existing:
        print("Badge already owned")
        return None

    # Get badge info
    query1 = """
    SELECT *
    FROM badges
    WHERE Badge_ID = %s
    """

    result = db_connect.execute_query_fetch(query1, (badge_id,))

    if not result:
        print("ERROR: Badge not found")
        return None

    points = result[0]["Badge_Points"]

    # Add points
    query2 = """
    UPDATE readers
    SET Points = Points + %s
    WHERE Reader_ID = %s
    """

    db_connect.execute_query(query2, (points, reader_ID))

    print("points added:", points)

    # Give badge
    query3 = """
    INSERT INTO given_badges(Badge_ID, Reader_ID)
    VALUES(%s, %s)
    """

    db_connect.execute_query(query3, (badge_id, reader_ID))

    return None

# Only use this for badges page
def get_all_badges():
    query1 = """
    SELECT *
    FROM badges
    """
    result = db_connect.execute_query_fetch(query1)
    return result


# From given badges join readers and badges and get badge information
def get_given_badges(reader_ID):
    query1 = """
    SELECT 
    badges.Badge_Name, 
    badges.Badge_Image_Path, 
    badges.Badge_Description, 
    badges.Badge_Rarity,
    badges.Badge_Points
    
    FROM given_badges gb
    JOIN badges     ON gb.Badge_ID = badges.Badge_ID
    JOIN readers r  ON gb.Reader_ID = r.Reader_ID
    WHERE r.Reader_ID = %s
    """
    result = db_connect.execute_query_fetch(query1, (reader_ID,))
    return result

def test_get_badge():
    print("Testing get_badge: ")
    reader_ID = 1
    badge_id = 2

def check_reader_badge(reader_ID):
    print("Testing check_reader_badge: ")
    query1="""
    SELECT Books_Read FROM readers WHERE Reader_ID = %s
    """
    result = db_connect.execute_query_fetch(query1, (reader_ID,))
    if 1 <= result[0]["Books_Read"] < 5:
        reader_get_badge(reader_ID, 1)
    elif 5 <= result[0]["Books_Read"] < 20:
        reader_get_badge(reader_ID, 2)
    elif 20 <= result[0]["Books_Read"] < 50:
        reader_get_badge(reader_ID, 3)
    elif 50 <= result[0]["Books_Read"] < 200:
        reader_get_badge(reader_ID, 4)
    elif 200 <= result[0]["Books_Read"] < 500:
        reader_get_badge(reader_ID, 5)
    elif 500 <= result[0]["Books_Read"]:
        reader_get_badge(reader_ID, 6)


def reader_add_books_read(reader_ID):
    print("Testing reader_add_books_read: ")
    query1 = """
    UPDATE readers
    SET Books_Read = Books_Read + 1
    WHERE Reader_ID = %s
    """
    check_reader_badge(reader_ID)
    db_connect.execute_query(query1, (reader_ID,))