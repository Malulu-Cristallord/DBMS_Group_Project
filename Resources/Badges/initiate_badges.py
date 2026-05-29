from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    # webb: Allow this script to be executed directly from the project root.
    sys.path.insert(0, str(ROOT))

from Backend.DB_Stuff import db_connect

# name, image path, description, rarity, points
badge_read_01 = ("First Chapter", "Resources/Badges/Badge_Read_01.png", "Read your first book and record it on LibTrack", "common", 10)
badge_read_02 = ("Handful of Knowledge", "Resources/Badges/Badge_Read_02.png", "Read and record 5 reading sessions on LibTrack", "common", 20)
badge_read_03 = ("Open Your Horizons", "Resources/Badges/Badge_Read_03.png", "Read and record 20 reading sessions on LibTrack", "common", 40)
badge_read_04 = ("Your Adventures in Readingland", "Resources/Badges/Badge_Read_04.png", "Read and record 50 reading sessions on LibTrack", "uncommon", 100)
badge_read_05 = ("The Reading Games", "Resources/Badges/Badge_Read_05.png", "Read and record 200 reading sessions on LibTrack", "rare", 200)
badge_read_06 = ("The Lord of the Books", "Resources/Badges/Badge_Read_06.png", "Read and record 500 reading sessions on LibTrack", "legendary", 500)
badges_read = (badge_read_01, badge_read_02, badge_read_03, badge_read_04, badge_read_05, badge_read_06)

#badge_review_and_post_01 = ("Critic's Pen", "Resources/Badges/Badge_Review&Post_01.png", "Publish your first review on LibTrack", "common", 20)
#badge_review_and_post_02 = ("Critic's Diary", "Resources/Badges/Badge_Review&Post_02.png", "Publish your first post on LibTrack", "common", 20)
#badges_review_and_post = (badge_review_and_post_01, badge_review_and_post_02)

#badge_add_books_01 = ("Knowledge Dripping Like a Faucet", "Resources/Badges/Badge_Add_Books_01.png", "Contribute 10 books to the LibTrack Database", "common", 40)
#badge_add_books_02 = ("Knowledge Flowing Like a Shower Head", "Resources/Badges/Badge_Add_Books_02.png", "Contribute 50 books to the LibTrack Database", "uncommon", 100)
#badge_add_books_03 = ("Knowledge Flooding Like a Storm", "Resources/Badges/Badge_Add_Books_03.png", "Contribute 200 books to the LibTrack Database", "rare", 200)
#badge_add_books_04 = ("Knowledge Invading Like a Sea", "Resources/Badges/Badge_Add_Books_04.png", "Contribute 500 books to the LibTrack Database", "legendary", 400)
#badges_add_books = (badge_add_books_01, badge_add_books_02, badge_add_books_03, badge_add_books_04)

all_badges = (*badges_read,)

# Waiting for change
def initiate_badges():
    # webb: Ensure the badges table exists before seeding badge rows.
    create_query = """
    CREATE TABLE IF NOT EXISTS badges (
        Badge_ID           INT              AUTO_INCREMENT PRIMARY KEY,
        Badge_Name         VARCHAR(255),
        Badge_Image_Path   VARCHAR(255),
        Badge_Description  TEXT,
        Badge_Rarity       VARCHAR(255),
        Badge_Points       INT
    )
    """
    error = db_connect.execute_query(create_query)
    if error:
        raise RuntimeError(error)

    query = """
    INSERT INTO badges(Badge_Name, Badge_Image_Path, Badge_Description, Badge_Rarity, Badge_Points)
    values(%s, %s, %s, %s, %s)
    """
    inserted = []
    skipped = []

    for badge in all_badges:
        # webb: Skip badges that already exist so repeated runs stay idempotent.
        existing = db_connect.execute_query_fetch(
            """
            SELECT Badge_ID
            FROM badges
            WHERE Badge_Name = %s
            LIMIT 1
            """,
            (badge[0],),
        )
        if existing is None:
            raise RuntimeError(f"Failed to check existing badge: {badge[0]}")
        if existing:
            print(f"Badge already exists, skipped: {badge[0]}")
            skipped.append(badge[0])
            continue

        values = (badge[0], badge[1], badge[2], badge[3], badge[4])
        error = db_connect.execute_query(query, values)
        if error:
            raise RuntimeError(error)

        print(f"Badge inserted: {badge[0]}")
        inserted.append(badge[0])

    print(
        "Badge initialization complete: "
        f"{len(inserted)} inserted, {len(skipped)} skipped."
    )
    return {"inserted": inserted, "skipped": skipped}


if __name__ == "__main__":
    # webb: Run badge initialization when this file is executed as a script.
    initiate_badges()
