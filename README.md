# LibTrack

LibTrack is an academic book discovery and reading community system built with
Streamlit, Python, and MySQL. It supports reader accounts, book importing,
personalized recommendations, saved books, reviews, posts, likes, comments,
reading timers, and badge rewards.

Creators of LibTrack: Maxence Cotonnec, 張家源, 潘又瑋, 龔亭安 
2026 All rights reserved. This project is for academic use only.

## Tech Stack

### Frontend / App Framework

- Streamlit multi-page app
- Custom Streamlit pages under `pages/`
- Shared UI helpers in `components/ui_helpers.py`
- Streamlit `session_state` for login/session state and temporary UI state

### Backend

- Python
- Function-based backend modules under `Backend/Functions/`
- MySQL access helpers under `Backend/DB_Stuff/`
- `mysql-connector-python` for database connection and SQL execution
- `bcrypt` for password hashing and login verification
- `requests` for Open Library API calls
- `authlib` and Streamlit auth config for optional Google OAuth support

### Database

- MySQL
- Main database name used by the app: `dbms_group_project`
- Local DB connection defaults:
  - host: `localhost`
  - user: `root`
  - password: `DB_PASSWORD` environment variable
  - database: `dbms_group_project`

### External API

- Open Library API for importing book metadata by ISBN
- Open Library Covers API for book cover images

## System Features

### Reader Accounts

- Reader registration with name, Gmail address, password, and preferred genres
- Password validation and bcrypt password hashing
- Login with email/password
- Login state stored in Streamlit `session_state`
- Reader settings for preferred genres and recommendation preference

Related files:

- `pages/01_Login.py`
- `pages/02_Register.py`
- `UI/Login/auth.py`
- `UI/Login/session.py`
- `UI/Login/validators.py`

### Book Discovery and Book Management

- Browse books from the MySQL `books` table
- Search by title, author, or genre
- Sort books by rating, title, or published year
- View book detail pages
- Import books by ISBN through Open Library
- Store book title, ISBN, author, publisher, published year, genre, cover,
  description, rating, click count, save count, and review count

Related files:

- `pages/03_Discovery.py`
- `pages/11_Add_Books.py`
- `pages/15_Book_Detail.py`
- `Backend/Functions/book_request.py`
- `Backend/Functions/library_data.py`

### Recommendations

- Personalized recommendations based on:
  - book average rating
  - clicked count
  - saved count
  - reader preferred genres
- Popular book ranking based on rating, clicked count, and saved count
- Recommendation records can be generated into the `recommendations` table
- Recommendation status supports `unread`, `clicked`, and `saved`

Related files:

- `app.py`
- `pages/12_Recommendations.py`
- `Backend/Functions/library_data.py`
- `Tests/test_recommendation_scores.py`

### Saved Books

- Readers can save books to a personal saved list
- Duplicate saves are prevented
- A reader can save up to 20 books
- Saving or deleting a book updates the book's saved count

Related files:

- `pages/17_Saved_Books.py`
- `Backend/Functions/saved_books.py`

### Reviews, Posts, Likes, and Comments

- Readers can write or update reviews for books
- Review submission updates book average rating and review count
- Readers can create posts and optionally link a post to a book
- Activity feed displays reader posts
- Posts support likes and comments

Related files:

- `pages/06_Create_Review.py`
- `pages/07_Create_Post.py`
- `pages/13_My_Posts.py`
- `pages/14_Edit_Post.py`
- `Backend/Functions/review_handler.py`
- `Backend/Functions/post_handler.py`

### Reading Timer and Badges

- Readers can record reading time with a timer
- Total reading time is stored on the reader record
- Reading sessions can increase `Books_Read`
- Badge rewards are stored in `badges` and `given_badges`
- Badge points update reader points

Related files:

- `pages/04_Record_Readings.py`
- `pages/05_Badges_Rewards.py`
- `Backend/Functions/reader.py`
- `Backend/Functions/badges_handler.py`
- `Resources/Badges/initiate_badges.py`

### Database Utilities

- Initial table creation helper
- Safer schema migration/check helper
- Read-only system integrity check
- Badge seed script
- ISBN seed import script

Related files:

- `Backend/DB_Stuff/initiate_database.py`
- `Backend/DB_Stuff/migrate_schema.py`
- `Tests/check_system_integrity.py`
- `Resources/Badges/initiate_badges.py`
- `Resources/Books/import_isbns.py`
- `docs/DB_MIGRATION_GUIDE.md`

## Backend Logic Guide

This section marks where the backend logic is written and explains how each
part supports the Streamlit pages. In this project, Streamlit pages are the UI,
while backend logic is mainly implemented as Python functions under
`Backend/Functions/`, `Backend/DB_Stuff/`, and `UI/Login/`.

### 1. Database Connection Layer

Backend logic location:

- `Backend/DB_Stuff/db_connect.py`

Explanation:

This file is the database access foundation of the project. The `get_connection`
function creates a MySQL connection to the local `dbms_group_project` database.
The helper functions `execute_query`, `execute_query_fetch`, `fetch_one`, and
`fetch_all` are used by other backend modules to run SQL statements. Write
operations commit changes to MySQL, while read operations return dictionary-like
rows that are easier for Streamlit pages to display.

Quick note:

`db_connect.py` is the bridge between Python backend functions and MySQL. If the
app cannot connect to the database, this is the first backend file to check.

### 2. Schema and Migration Logic

Backend logic location:

- `Backend/DB_Stuff/initiate_database.py`
- `Backend/DB_Stuff/migrate_schema.py`

Explanation:

`initiate_database.py` contains the original table creation logic. It defines
core tables such as `books`, `readers`, `posts`, `reviews`, `recommendations`,
`likes`, `comments`, `badges`, `saved_books`, and `given_badges`.

`migrate_schema.py` is the safer and more complete schema helper. It checks
whether expected tables, columns, and important unique indexes exist, then can
apply missing schema changes. It is useful when the local MySQL database is
older than the current code.

Quick note:

Use `migrate_schema.py` when the app fails because a table or column is missing.
It updates the database structure without deleting existing data.

### 3. Authentication and Session Logic

Backend logic location:

- `UI/Login/auth.py`
- `UI/Login/session.py`
- `UI/Login/validators.py`

Explanation:

`auth.py` handles registration, login, bcrypt password hashing, password
verification, and optional Google login synchronization. During registration,
the plain password is converted into a bcrypt hash and stored in
`readers.Password_Hash`. During login, the input password is checked against the
stored hash.

`session.py` writes login information into Streamlit `session_state`, including
`logged_in`, `reader_id`, `reader_name`, `reader_email`, `preferred_category`,
and `points`. Pages use this state to decide whether a reader is logged in.

`validators.py` checks email and password rules before registration.

Quick note:

The app never stores the plain password. It stores a bcrypt hash, then uses
`session_state` to remember which reader is currently logged in.

### 4. Reader and Profile Logic

Backend logic location:

- `Backend/Functions/library_data.py`

Explanation:

`library_data.py` contains reader-related helpers such as `get_reader_by_id`,
`get_reader_from_session`, `update_reader_profile`, and `get_reader_genres`.
These functions load reader profile data from MySQL, update reader settings, and
convert the reader's comma-separated preferred genres into a Python list.

The Streamlit pages use these functions to display profile information, apply
recommendation preferences, and check whether a page should show private reader
content.

Quick note:

Reader data is stored in MySQL, but Streamlit pages usually access it through
`get_reader_from_session()`.

### 5. Book Query and Book Normalization Logic

Backend logic location:

- `Backend/Functions/library_data.py`

Explanation:

Book display logic is also centralized in `library_data.py`. The `get_books`
function supports search, genre filtering, sorting, and optional limits.
`get_book_by_isbn` loads one book by ISBN. `normalize_book` converts raw MySQL
column names into consistent keys such as `title`, `isbn`, `author`, `genre`,
`cover`, `avg_rating`, `clicked`, `saved`, and `review_count`.

This normalization step is important because Streamlit pages can use stable
dictionary keys instead of dealing with raw database column names directly.

Quick note:

`normalize_book()` makes book data easier to use in the UI. It turns database
rows into clean Python dictionaries.

### 6. Open Library Import Logic

Backend logic location:

- `Backend/Functions/book_request.py`
- `Resources/Books/import_isbns.py`

Explanation:

`book_request.py` handles book import by ISBN. The import flow first checks
whether the ISBN already exists in the `books` table. If not, it calls Open
Library's ISBN endpoint, extracts useful fields, cleans missing or inconsistent
values, builds a cover URL when possible, and writes the cleaned data into
MySQL.

The cleaned fields include title, ISBN, author, description, publisher,
published year, cover, genre, and gathered source. `Resources/Books/import_isbns.py`
reuses this import flow to seed several sample ISBNs into the database.

Quick note:

Open Library returns raw JSON. `book_request.py` selects only the fields the app
needs, handles missing data, and inserts a clean row into `books`.

### 7. Recommendation Logic

Backend logic location:

- `Backend/Functions/library_data.py`
- `Tests/test_recommendation_scores.py`

Explanation:

Recommendation logic is implemented in `library_data.py`. The system first
loads candidate books from the `books` table, then calculates recommendation
scores. Personalized recommendations use four factors: book rating, clicked
count, saved count, and whether the book genre matches the reader's preferred
genres.

The personalized score uses these weights:

- rating: 0.4
- clicked count: 0.2
- saved count: 0.2
- preferred genre match: 0.2

Popular books use rating, clicked count, and saved count, but do not use reader
preference. `generate_recommendations_for_reader` can write generated results
into the `recommendations` table, while `get_personalized_recommendations` can
calculate recommendations directly for display.

Quick note:

Recommendations are not random. They are score-based and use both book behavior
data and the reader's preferred genres.

### 8. Saved Books Logic

Backend logic location:

- `Backend/Functions/saved_books.py`

Explanation:

`saved_books.py` manages the saved book feature. It checks whether a reader has
already saved a book, counts how many books the reader has saved, inserts new
saved-book records, and removes saved books. When a book is saved or removed,
the backend also updates the `books.Saved` counter.

The saved relationship is stored in the `saved_books` table because one reader
can save many books and one book can be saved by many readers.

Quick note:

`saved_books.py` is a many-to-many relationship handler between readers and
books.

### 9. Review Logic

Backend logic location:

- `Backend/Functions/review_handler.py`

Explanation:

`review_handler.py` handles book reviews. `create_review` checks whether the
same reader has already reviewed the same book. If a review exists, it updates
the old review. If not, it inserts a new review. After every review change, the
backend updates the book's average rating and review count.

`get_reviews` uses joins to return review content together with reader and book
information, which allows the UI to show the reviewer name, book title, author,
rating, and review content.

Quick note:

A review is linked to both a reader and a book. Updating reviews also updates
book-level statistics.

### 10. Post, Like, and Comment Logic

Backend logic location:

- `Backend/Functions/post_handler.py`
- `Backend/Functions/library_data.py`

Explanation:

`post_handler.py` creates, updates, deletes, and loads posts. A post belongs to
a reader and may optionally link to a book through ISBN. The same file also
handles likes and comments. Likes are inserted into the `likes` table, and
comments are inserted into the `comments` table.

`library_data.py` also provides `get_posts`, which joins `posts`, `readers`, and
`books` so the activity feed can display the post content together with the
reader name and book information.

Quick note:

Posts store the activity itself, while likes and comments store social
interactions around each post.

### 11. Reading Timer Logic

Backend logic location:

- `Backend/Functions/reader.py`
- `pages/04_Record_Readings.py`

Explanation:

The reading timer UI is written in `pages/04_Record_Readings.py`. It uses
Streamlit `session_state` to track whether the timer is running, when it
started, and how many seconds have elapsed. When the reader saves a session,
`save_reading_session_time` in `reader.py` converts seconds into `HH:MM:SS` and
adds that duration to `readers.Time_Read`.

Longer reading sessions can also increase the reader's `Books_Read` value and
trigger badge checks.

Quick note:

Timer state is temporary in Streamlit, but saved reading time is accumulated in
the `readers` table.

### 12. Badge and Points Logic

Backend logic location:

- `Backend/Functions/badges_handler.py`
- `Backend/Functions/library_data.py`
- `Resources/Badges/initiate_badges.py`

Explanation:

`initiate_badges.py` seeds badge definitions into the `badges` table.
`badges_handler.py` checks whether a reader already owns a badge, awards new
badges through the `given_badges` table, and adds badge points to
`readers.Points`.

`library_data.py` provides helper functions to load earned badges and locked
badges for display on the badges page.

Quick note:

`badges` defines what badges exist. `given_badges` records which reader has
earned which badge.

### 13. JOIN Query Usage

Backend logic location:

- `Backend/Functions/library_data.py`
- `Backend/Functions/saved_books.py`
- `Backend/Functions/review_handler.py`
- `Backend/Functions/post_handler.py`

Explanation:

JOIN queries are used whenever the app needs data from multiple tables at the
same time. For example, saved books join `saved_books` with `books`; reviews
join `reviews`, `readers`, and `books`; posts join `posts`, `readers`, and
`books`; comments join `comments` with `readers`; recommendations join
`recommendations` with `books`; badges join `given_badges`, `badges`, and
`readers`.

This keeps tables normalized while still allowing the UI to display complete
information.

Quick note:

Most relationship tables only store IDs. JOIN queries turn those IDs into
readable information such as reader names, book titles, covers, and badge names.

## Database Tables

The current MySQL schema is centered around these tables:

- `readers`: reader accounts, password hashes, preferences, points, reading data
- `books`: book metadata imported from Open Library or stored locally
- `posts`: reader posts, optionally linked to books
- `reviews`: reader book reviews and ratings
- `recommendations`: generated recommendation results per reader and book
- `saved_books`: reader saved books
- `likes`: post likes
- `comments`: post comments
- `badges`: badge definitions
- `given_badges`: badges awarded to readers

The latest schema definition is maintained in:

```bash
Backend/DB_Stuff/migrate_schema.py
```

## Installation

### 1. Clone the project

```bash
git clone <repository-url>
cd DBMS_Group_Project
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r requirement.txt
```

The app also imports `requests` and `streamlit-autorefresh`. If they are not
already installed in your environment, install them as well:

```bash
pip install requests streamlit-autorefresh
```

### 4. Create the MySQL database

Start MySQL, then create the local database:

```sql
CREATE DATABASE dbms_group_project;
```

### 5. Set database environment variables

The app reads the MySQL password from `DB_PASSWORD`.

For macOS/Linux:

```bash
export DB_PASSWORD="your_mysql_password"
```

Optional variables used by the migration helper:

```bash
export DB_HOST="localhost"
export DB_PORT="3306"
export DB_USER="root"
export DB_NAME="dbms_group_project"
```

Note: `Backend/DB_Stuff/db_connect.py` currently uses `localhost`, `root`, and
`dbms_group_project` directly. Make sure those match your local MySQL setup.

### 6. Create or migrate database tables

Run a dry-run first:

```bash
.venv/bin/python Backend/DB_Stuff/migrate_schema.py
```

If the output looks correct, apply the migration:

```bash
.venv/bin/python Backend/DB_Stuff/migrate_schema.py --apply
```

Optional: add recommended duplicate-prevention indexes when your local data has
no duplicates:

```bash
.venv/bin/python Backend/DB_Stuff/migrate_schema.py --apply --with-recommended-uniques
```

### 7. Seed badge data

```bash
.venv/bin/python Resources/Badges/initiate_badges.py
```

### 8. Optional: import sample books by ISBN

```bash
.venv/bin/python Resources/Books/import_isbns.py
```

This script imports a fixed list of ISBNs through Open Library.

### 9. Optional: run database integrity checks

```bash
.venv/bin/python Tests/check_system_integrity.py
```

### 10. Start the Streamlit app

```bash
.venv/bin/streamlit run app.py
```

Open the URL printed by Streamlit, usually:

```text
http://localhost:8501
```

## Optional Google OAuth Setup

An example Streamlit secrets file is available at:

```bash
.streamlit/secrets.example.toml
```

To use Google login, create your own `.streamlit/secrets.toml` and fill in:

- `auth.redirect_uri`
- `auth.cookie_secret`
- `auth.google.client_id`
- `auth.google.client_secret`
- `auth.google.server_metadata_url`

Email/password login works without Google OAuth.

## Useful Commands

Run the app:

```bash
.venv/bin/streamlit run app.py
```

Check schema without changing the database:

```bash
.venv/bin/python Backend/DB_Stuff/migrate_schema.py
```

Apply safe schema changes:

```bash
.venv/bin/python Backend/DB_Stuff/migrate_schema.py --apply
```

Run integrity checks:

```bash
.venv/bin/python Tests/check_system_integrity.py
```

Seed badges:

```bash
.venv/bin/python Resources/Badges/initiate_badges.py
```

Import sample ISBNs:

```bash
.venv/bin/python Resources/Books/import_isbns.py
```

## Project Structure

```text
DBMS_Group_Project/
├── app.py
├── pages/
├── components/
├── UI/Login/
├── Backend/
│   ├── DB_Stuff/
│   └── Functions/
├── Resources/
│   ├── Badges/
│   ├── Book Covers/
│   └── Books/
├── Tests/
├── ERD/
├── docs/
└── requirement.txt
```

## Notes

- This project currently uses Streamlit pages that directly call Python backend
  functions. It does not expose a separate Flask, FastAPI, Express, or REST API
  server yet.
- The database is designed for local MySQL development. For cloud deployment,
  update the DB connection settings and move credentials to environment
  variables or Streamlit secrets.
- Open Library does not require an API key for the current ISBN import flow.
