# ERD Compliance Checklist

Source of truth: final ERD image provided in the conversation on 2026-05-28.

Audit scope:
- Database initializer: `Backend/DB_Stuff/initiate_database.py`
- DB connection/query helpers: `Backend/DB_Stuff/db_connect.py`
- Backend logic: `Backend/Functions/*`
- Authentication/session flow: `UI/Login/*`, `pages/01_Login.py`, `pages/02_Register.py`
- Streamlit pages: `app.py`, `pages/*`
- Existing tests and docs: `Tests/*`, `README.md`, `TODO.txt`

Live database note: a read-only schema introspection was attempted, but MySQL was not reachable at `localhost:3306`. This checklist is based on checked-in schema and code. Run `Tests/check_system_integrity.py` after starting MySQL to compare the live database.

## Naming Compatibility Policy

The ERD uses mostly snake_case names, while the current MySQL schema uses PascalCase column names. Most differences are naming-style differences only and are safer to handle through compatibility aliases in Python/docs rather than immediate schema renames.

The main non-style mismatches are:
- `READER.point` is stored as `readers.Points`.
- `READER.create_at` is stored as `readers.Created_At`.
- `BOOK.Publish_year` is stored as `books.Published_Year`.
- `GIVEN_BADGES.given_badges_id` is stored as `given_badges.Given_Badge_ID`.

No schema migration was applied in this pass.

## Entity Checklist

| ERD entity / relationship | Expected fields | Current implementation status | Missing fields or mismatched names | Related files/functions | Compliance | Suggested fix |
|---|---|---|---|---|---|---|
| `READER` | `reader_id`, `name`, `email`, `password_hash`, `Google_sub`, `preferred_category`, `books_read`, `receive_recommendations`, `show_reading_history`, `point`, `daily_time_goal`, `create_at` | Table `readers` exists. Registration, login, Google login, profile/settings, session identity are implemented. Email has `UNIQUE`. Passwords are hashed with bcrypt. | Stored as `Reader_ID`, `Name`, `Email`, `Password_Hash`, `Google_Sub`, `Preferred_Category`, `Books_Read`, `Receive_Recommendations`, `Show_Reading_History`, `Points`, `Daily_Time_Goal`, `Created_At`. Extra fields: `Time_Read`, `Books_Added`. Login previously did not normalize email before lookup. | `initiate_readers`, `register_reader`, `login_reader`, `login_or_register_google_reader`, `set_reader_session`, `get_reader_by_id`, `update_reader_profile` | Partially compliant | Keep current schema. Normalize login email. Document aliases. Consider adding reader aliases for `books_read` and `create_at` if more pages need snake_case. |
| `BOOK` | `ISBN`, `title`, `author`, `Publisher`, `Publish_year`, `cover`, `description`, `genre`, `saved`, `gathered_at`, `average_rating`, `review_count`, `clicked` | Table `books` exists. Discovery, detail, add book, popular books, recommendation scoring, click count, save count, and review aggregate logic exist. | Stored as `Title`, `Author`, `Published_Year`, `Cover`, `Description`, `Genre`, `Saved`, `Gathered_At`, `Average_Rating`, `Review_Count`, `Clicked`. `Publish_year` vs `Published_Year` is the most meaningful mismatch. | `initiate_books`, `get_books`, `get_book_by_isbn`, `get_books_for_recommendation`, `request_book_data`, `increment_book_clicked`, `update_book_review_stats` | Mostly compliant | Keep current schema and compatibility aliases. Avoid renaming until a real migration is planned. |
| `BOOK_SAVED` | `save_id`, `save_book_isbn`, `save_to_reader_id` | Table `saved_books` exists. Reader/book many-to-many save relation exists. App checks duplicates and DB has `UNIQUE KEY unique_saved_book`. Save/delete updates `books.Saved`. | Stored as `Save_ID`, `Saved_Book_ISBN`, `Saved_To_Reader_ID`. Table name is `saved_books`, not `BOOK_SAVED`. | `initiate_saved_books`, `save_book`, `is_book_saved`, `delete_saved_book`, `get_saved_books`, `pages/17_Saved_Books.py` | Mostly compliant | Keep current schema. The duplicate rule is enforced well enough for current use. |
| `RECOMMENDATION` | `recommendation_id`, `reader_id`, `ISBN`, `score`, `generated_at`, `reason`, `status` | Table `recommendations` exists. DB rows connect one reader to one book and have unique `(Reader_ID, ISBN)`. Existing score formula uses rating, clicked, saved, and preferred-category match. Reason is generated. Status updates to `clicked` or `saved`. | Stored as PascalCase. Status default is `unread`; ERD examples mention statuses such as active/clicked/dismissed/saved. Home page can show transient recommendations without persisting rows. | `initiate_recommendations`, `calculate_personalized_score`, `generate_recommendations_for_reader`, `get_recommendations_for_reader`, `update_recommendation_status`, `pages/12_Recommendations.py`, `app.py` | Mostly compliant | Do not create another formula. Keep current formula. Consider renaming status `unread` to `active` only through a planned migration/UI update. |
| `REVIEWS` | `review_id`, `reader_id`, `ISBN`, `content`, `rating`, `create_at` | Table `reviews` exists. Reader can create a review. Existing review by same reader/book is updated in app logic. Book average/rating count is recalculated after create/update. | Stored as `Review_ID`, `Reader_ID`, `Content`, `Rating`, `Created_At`. No DB unique constraint on `(Reader_ID, ISBN)`. Backend does not validate rating range, though UI slider limits it. | `initiate_reviews`, `create_review`, `get_reviews`, `get_review_by_reader_and_book`, `update_book_review_stats`, `pages/06_Create_Review.py`, `pages/15_Book_Detail.py` | Partially compliant | Keep app-level update behavior. Later add unique `(Reader_ID, ISBN)` and backend rating validation if concurrency/data integrity matters. |
| `POST` | `post_id`, `reader_id`, `ISBN`, `content`, `created_date` | Table `posts` exists. Reader can create/edit/delete posts. Posts can optionally link to books. Activity feed, profile, my posts, and reading history read posts. | Stored as `Post_ID`, `Reader_ID`, `ISBN`, `Content`, `Created_Date`. `pages/07_Create_Post.py` contains a debug `st.write(books)`. | `initiate_posts`, `create_post`, `update_post`, `delete_post`, `get_posts`, `get_posts_by_reader`, `pages/07_Create_Post.py`, `pages/13_My_Posts.py`, `pages/14_Edit_Post.py` | Mostly compliant | Leave schema. Optional UI cleanup later. |
| `LIKE` | `like_id`, `post_id`, `reader_id` | Table `likes` exists. Reader can like/unlike posts. Activity feed shows counts and toggles state. | Stored as `Like_ID`, `Post_ID`, `Reader_ID`. No DB unique constraint on `(Post_ID, Reader_ID)`. `INSERT IGNORE` will not prevent duplicates without a unique key. | `initiate_likes`, `add_like`, `remove_like`, `has_liked`, `get_like_count`, `app.py` | Partially compliant | Later add unique `(Post_ID, Reader_ID)` or add a handler-level duplicate check before insert. |
| `COMMENT` | `comment_id`, `post_id`, `reader_id`, `content`, `create_at` | Table `comments` exists. Reader can comment on posts. Activity feed displays comments. | Stored as `Comment_ID`, `Post_ID`, `Reader_ID`, `Content`, `Created_At`. | `initiate_comments`, `create_comment`, `get_comments`, `app.py` | Mostly compliant | Keep compatibility naming note. |
| `BADGES` | `badge_id`, `badge_name`, `badge_description`, `badge_image_path`, `badge_rarity`, `badge_points` | Table `badges` exists. Seed script exists. Backend handlers can list badges. | Stored as PascalCase. Badges page uses hardcoded/mock badge data rather than DB rows. | `initiate_badges`, `Resources/Badges/initiate_badges.py`, `get_all_badges`, `pages/05_Badges_Rewards.py` | Partially compliant | Keep schema. Later connect Badges page to `badges` and `given_badges`. |
| `GIVEN_BADGES` | `given_badges_id`, `reader_id`, `badge_id` | Table `given_badges` exists. Backend handler can assign badges and checks for existing assignment before insert. | Stored as `Given_Badge_ID`, `Reader_ID`, `Badge_ID`. Extra field: `Given_Time`. No DB unique constraint on `(Reader_ID, Badge_ID)`. Assignment triggers are not fully wired into pages. | `initiate_given_badges`, `reader_get_badge`, `get_given_badges`, `check_for_badge_book_adding` | Partially compliant | Later add unique `(Reader_ID, Badge_ID)` and wire real achievement triggers. |

## Relationship Checks

| Relationship | Current implementation | Status | Notes |
|---|---|---|---|
| Reader registers/logs in | Implemented through `register_reader`, `login_reader`, Streamlit login/register pages, and session helpers. | Fixed in this pass | Email normalization was inconsistent before the fix. |
| Reader to saved books | `saved_books` joins `readers` and `books`, with FK constraints and unique save pair. | Mostly compliant | Save/delete also updates `books.Saved`. |
| Reader to recommendations | `recommendations.Reader_ID` FK and recommendation generation/read/status helpers. | Mostly compliant | Home page recommendation cards are calculated directly and are not always persisted. |
| Book to recommendations | `recommendations.ISBN` FK. | Mostly compliant | Status is updated only if a DB recommendation row exists. |
| Reader to reviews | `reviews.Reader_ID` FK and create/update logic. | Partially compliant | App prevents duplicates by update, but DB does not enforce unique reader/book review. |
| Book to reviews | `reviews.ISBN` FK and aggregate update into `books.Average_Rating` / `Review_Count`. | Mostly compliant | Aggregates depend on create/update path calling `update_book_review_stats`. |
| Reader to posts | `posts.Reader_ID` FK and post CRUD. | Mostly compliant | Delete manually deletes comments/likes first. |
| Book to posts | `posts.ISBN` FK and optional link in create/edit post. | Mostly compliant | UI linking flow is implemented but has debug output. |
| Post to likes | `likes.Post_ID` FK and like count/toggle. | Partially compliant | Needs unique pair for DB-level duplicate protection. |
| Reader to likes | `likes.Reader_ID` FK. | Partially compliant | Same duplicate concern. |
| Post to comments | `comments.Post_ID` FK and comment display. | Mostly compliant | No major logic gap found. |
| Reader to comments | `comments.Reader_ID` FK. | Mostly compliant | No major logic gap found. |
| Badge to given badges | `given_badges.Badge_ID` FK. | Partially compliant | Handler exists, UI mostly mock. |
| Reader to given badges | `given_badges.Reader_ID` FK. | Partially compliant | Needs DB unique pair and better page integration. |

## Implemented / Partial / Missing

Implemented or mostly implemented:
- Email/password registration and login
- Google login compatibility path
- Book discovery/detail/add book
- Saved books
- Recommendations with existing score formula
- Reviews with book aggregate updates
- Posts, likes, comments
- Badge tables and seed data

Partially implemented:
- Badge UI and real badge assignment triggers
- DB-level duplicate prevention for likes, reviews, and given badges
- Persistent recommendation lifecycle outside the Recommendations page
- Exact ERD naming alignment

Not implemented or not found:
- A schema migration that normalizes column names to exact ERD snake_case
- DB-backed Badges page rendering
- Dismissed recommendation status
- Persistent reading session/history table beyond `readers.Time_Read` and post-based activity display
