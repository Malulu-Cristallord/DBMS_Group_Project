# System Test Guide

This guide is for manual Streamlit UI testing plus lightweight database verification.

## Setup

1. Start MySQL locally and make sure the database exists:

   ```bash
   mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS dbms_group_project;"
   ```

2. Load the DB password into your shell. If `.env` contains `DB_PASSWORD=...`, use:

   ```bash
   set -a
   source .env
   set +a
   ```

3. Initialize tables if needed:

   ```bash
   .venv/bin/python Backend/DB_Stuff/initiate_database.py
   ```

   Type `full` when prompted.

4. Run the read-only integrity check:

   ```bash
   .venv/bin/python Tests/check_system_integrity.py
   ```

5. Run the app:

   ```bash
   .venv/bin/streamlit run app.py
   ```

## Manual Test Cases

Use a new Gmail-style email for clean tests, for example `libtrack.test.20260528@gmail.com`.

| Test case | Precondition | Steps | Expected result | DB table(s) that should change | How to verify |
|---|---|---|---|---|---|
| Register new reader | App is running; email does not exist in `readers`. | Open Register. Enter name, Gmail email, valid password such as `ReaderA1!`, confirm password, choose at least one genre, submit. | Registration succeeds and redirects to Login. | `readers` inserts one row. | Query `SELECT Reader_ID, Email, Password_Hash, Preferred_Category FROM readers WHERE Email = '...';`. `Password_Hash` should start with `$2`. |
| Login with new reader | Reader was just registered. | Open Login. Enter the same email and password. Also try mixed-case email with spaces, for example `  LibTrack.Test.20260528@GMAIL.COM  `. | Login succeeds and app opens home page. Session should identify the reader. | No table must change just from login. | UI shows home page with reader name. Optional DB check confirms row still has normalized lowercase email. |
| Login with wrong password | Reader exists. | Open Login. Enter registered email and an incorrect password. | Login fails with incorrect password message. | No table should change. | UI remains on Login. Confirm no new `readers` row was inserted. |
| Duplicate email registration | Reader exists. | Open Register. Enter the same email with valid form data. | Registration is rejected with duplicate email message. | No new `readers` row. | `SELECT COUNT(*) FROM readers WHERE Email = '...';` remains `1`. |
| Book discovery | At least one row exists in `books`. | Open Discovery. Search by title/author/genre. Sort by rating/title/year. Click Details. | Matching books display. Details page opens. | `books.Clicked` increments when Details is clicked. | Check `SELECT Clicked FROM books WHERE ISBN = '...';` before and after. |
| Saving a book | Reader is logged in; at least one book exists. | In Discovery/Home/Recommendations, click Save on a book. Try saving it again. | First save succeeds. Second save says already saved. | `saved_books` inserts one row; `books.Saved` increments once. | Check `saved_books` for `(Saved_Book_ISBN, Saved_To_Reader_ID)` and `books.Saved`. |
| Recommendation display | Reader is logged in and books exist. | Open Recommendations. Click Generate Recommendations. View listed recommendations. | Recommendation rows display with score, reason, and status. | `recommendations` inserts rows with `Score`, `Reason`, `Status`. | Query `SELECT * FROM recommendations WHERE Reader_ID = ... ORDER BY Score DESC;`. |
| Recommendation view/save status | Recommendations exist. | Click View on a recommendation. Return, then Save a recommendation. | View changes status to `clicked`; Save changes status to `saved` if row exists. | `recommendations.Status`, `books.Clicked`, `saved_books`, `books.Saved`. | Query recommendation row by `Reader_ID` and `ISBN`. |
| Review creation | Reader is logged in; book exists. | Open Write Review. Select book, choose rating, enter content, submit. Submit again with changed text/rating. | First submit creates review. Second submit updates existing review. | `reviews` inserts or updates one row; `books.Average_Rating` and `books.Review_Count` update. | Query `reviews` by `Reader_ID` and `ISBN`; query book aggregate fields. |
| Post creation | Reader is logged in; book may exist. | Open Create a Post. Enter content. Optionally link a book by title or ISBN. Publish. | Post appears in activity feed and My Posts. | `posts` inserts one row. | Query `SELECT * FROM posts WHERE Reader_ID = ... ORDER BY Created_Date DESC;`. |
| Like post | At least one post exists from any reader. | On home activity feed, click the heart/like button. Click again to unlike. | Count increases once, then decreases. | `likes` inserts one row, then deletes it. | Query `SELECT COUNT(*) FROM likes WHERE Post_ID = ... AND Reader_ID = ...;`. Note: DB currently lacks a unique pair constraint. |
| Comment post | At least one post exists. | On home activity feed, open Comments. Enter a comment and click Post. | Comment appears under the post. | `comments` inserts one row. | Query `SELECT * FROM comments WHERE Post_ID = ... ORDER BY Created_At DESC;`. |
| Badge assignment | `badges` and `given_badges` tables exist. | Use backend handler or any page trigger that calls `reader_get_badge(reader_id, badge_id)`. Then open badges/profile pages. | Handler should add badge once and increase reader points. Current Badges page is mostly mock data, so UI may not reflect DB assignment. | `given_badges` inserts one row; `readers.Points` increases. | Query `given_badges` and `readers.Points`. Run integrity check for duplicate badge assignments. |
| Logout | Reader is logged in. | Use the Account section in the Navigation area and click Log out. | Session is cleared and Login page opens. | No table should change. | Protected pages should show sign-in required after logout. |

## Useful SQL Checks

Replace placeholders before running.

```sql
SELECT Reader_ID, Email, Password_Hash, Preferred_Category
FROM readers
WHERE Email = 'reader@gmail.com';

SELECT Saved_Book_ISBN, Saved_To_Reader_ID, COUNT(*) AS total
FROM saved_books
GROUP BY Saved_Book_ISBN, Saved_To_Reader_ID
HAVING COUNT(*) > 1;

SELECT Reader_ID, ISBN, Score, Reason, Status
FROM recommendations
WHERE Reader_ID = 1
ORDER BY Score DESC;

SELECT ISBN, Average_Rating, Review_Count
FROM books
WHERE ISBN = '9780439362139';

SELECT Reader_ID, ISBN, COUNT(*) AS total
FROM reviews
GROUP BY Reader_ID, ISBN
HAVING COUNT(*) > 1;
```

## Pass Criteria

The system passes the core manual check if:
- A newly registered reader can log in with the same password.
- Wrong password does not log in.
- Duplicate email is blocked.
- Book discovery, save, recommendation, review, post, like, and comment flows can be completed without Streamlit errors.
- `Tests/check_system_integrity.py` reports no missing required ERD tables/columns. Warnings are acceptable for known partial items listed in `docs/ERD_COMPLIANCE_CHECKLIST.md`.
