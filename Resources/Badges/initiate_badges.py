from Backend.DB_Stuff import db_connect

# name, image path, description, rarity, points
badge_read_01 = ("First Chapter", "Resources/Badges/Badge_Read_01.png", "Read your first book and record it on LibTrack", "common", 10)
badge_read_02 = ("Handful of Knowledge", "Resources/Badges/Badge_Read_02.png", "Read and record 5 reading sessions on LibTrack", "common", 20)
badge_read_03 = ("Open Your Horizons", "Resources/Badges/Badge_Read_03.png", "Read and record 20 reading sessions on LibTrack", "common", 40)
badge_read_04 = ("Your Adventures in Readingland", "Resources/Badges/Badge_Read_04.png", "Read your first book and record it on LibTrack", "uncommon", 100)
badge_read_05 = ("The Reading Games", "Resources/Badges/Badge_Read_05.png", "Read and record 5 reading sessions on LibTrack", "rare", 200)
badge_read_06 = ("The Lord of the Books", "Resources/Badges/Badge_Read_06.png", "Read and record 20 reading sessions on LibTrack", "legendary", 500)
badges_read = (badge_read_01, badge_read_02, badge_read_03, badge_read_04, badge_read_05, badge_read_06)

badge_review_01 = ("Critic's Pen", )

def initiate_badges():
    query = """
    INSERT INTO badges(Badge_Name, Badge_Image_Path, Badge_Description, Badge_Rarity, Badge_Points)
    values(%s, %s, %s, %s, %d)
    """
    db_connect.execute_query(query)
