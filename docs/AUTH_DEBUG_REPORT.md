# Authentication Debug Report

Date: 2026-05-28

## Reported Issue

After registering a new account, the user may be unable to log in.

## Registration Flow

1. `pages/02_Register.py` collects name, email, password, confirmation, preferred genres, and recommendation preference.
2. The page normalizes email with `(email_input or "").strip().lower()`.
3. The page validates Gmail-format email and password strength.
4. `UI/Login/auth.py::register_reader` normalizes email again.
5. `register_reader` checks duplicate email with `SELECT Reader_ID FROM readers WHERE Email = %s`.
6. `register_reader` hashes the password with bcrypt through `hash_password`.
7. `register_reader` inserts into `readers.Name`, `readers.Email`, `readers.Password_Hash`, `readers.Preferred_Category`, and `readers.Receive_Recommendations`.
8. The transaction is committed.
9. The Register page redirects to `pages/01_Login.py`.

## Login Flow

1. `pages/01_Login.py` collects email and password.
2. The page passes raw form values to `UI/Login/auth.py::login_reader`.
3. `login_reader` queries `readers` by email.
4. If a row is found, `verify_password` checks the entered password against `readers.Password_Hash` using bcrypt.
5. On success, `pages/01_Login.py` calls `set_reader_session`.
6. `set_reader_session` stores:
   - `logged_in`
   - `reader_id`
   - `reader_name`
   - `reader_email`
   - `preferred_category`
   - `points`
7. The page switches to `app.py`.

## Root Cause

Registration stored a normalized lowercase email, but login previously queried with the raw email typed into the login form.

Example:

- Registered/stored email: `reader@gmail.com`
- Login input: `  Reader@GMAIL.COM  `
- Previous DB lookup: `WHERE Email = '  Reader@GMAIL.COM  '`
- Result: no row found, so login failed with "Reader account not found."

Password hashing and verification were not the root cause in the current code. Registration stores `Password_Hash` using bcrypt, and login verifies with `bcrypt.checkpw`.

Google login was not the root cause either. `Google_Sub` is optional for normal email/password accounts and is not required by the normal login query.

## Affected Files / Functions

- `pages/02_Register.py`
  - Normalizes email before calling `register_reader`.
- `UI/Login/auth.py::register_reader`
  - Normalizes email before duplicate check and insert.
- `pages/01_Login.py`
  - Passes login form values to `login_reader`.
- `UI/Login/auth.py::login_reader`
  - Previously did not normalize email before lookup.
- `UI/Login/session.py::set_reader_session`
  - Stores successful reader identity into Streamlit session state.

## Fix

`UI/Login/auth.py::login_reader` now normalizes email with the same rule used by registration:

```python
clean_email = (email or "").strip().lower()
```

The login query now uses `clean_email` instead of the raw form input.

## Verification

Automated check:

```bash
.venv/bin/python -m unittest Tests/test_auth_validation.py
```

The added test verifies that `login_reader("  Reader@GMAIL.COM  ", "ReaderA1!")` queries the database using `reader@gmail.com`.

Manual check:

1. Register a new reader with a Gmail address and a valid password.
2. Go to Login.
3. Enter the same email with different casing and surrounding spaces.
4. Enter the correct password.
5. Login should succeed and redirect to `app.py`.

Negative check:

1. Repeat login with the same normalized email but wrong password.
2. Login should fail with "Incorrect password."
