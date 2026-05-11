# Login, registration, and password helpers for readers.

import secrets

import bcrypt

from Backend.DB_Stuff.db_connect import get_connection
from UI.Login.validators import validate_google_email, validate_password


READER_SELECT_COLUMNS = """
    Reader_ID,
    Name,
    Email,
    Preferred_Category,
    Points,
    Receive_Recommendations,
    Show_Reading_History,
    Created_At,
    Google_Sub
"""


def hash_password(password: str) -> str:
    hashed_bytes = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    )
    return hashed_bytes.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8"),
    )


def _claim(user_info: dict, key: str):
    if hasattr(user_info, "get"):
        return user_info.get(key)
    return getattr(user_info, key, None)


def _is_truthy(value) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in {"1", "true", "yes"}
    return bool(value)


def _ensure_google_sub_column(cursor) -> None:
    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM information_schema.columns
        WHERE table_schema = DATABASE()
          AND table_name = 'readers'
          AND column_name = 'Google_Sub'
        """
    )
    row = cursor.fetchone() or {}

    if int(row.get("total") or 0) == 0:
        cursor.execute(
            """
            ALTER TABLE readers
            ADD COLUMN Google_Sub VARCHAR(255) NULL UNIQUE AFTER Email
            """
        )


def _google_reader_name(user_info: dict, email: str) -> str:
    name = (_claim(user_info, "name") or "").strip()
    if name:
        return name

    given_name = (_claim(user_info, "given_name") or "").strip()
    family_name = (_claim(user_info, "family_name") or "").strip()
    full_name = " ".join(part for part in [given_name, family_name] if part)
    if full_name:
        return full_name

    return email.split("@", maxsplit=1)[0]


def register_reader(
    name: str,
    email: str,
    password: str,
    preferred_category: str | None = None,
    receive_recommendations: bool = True,
) -> tuple[bool, str]:
    clean_email = (email or "").strip().lower()

    email_is_valid, email_message = validate_google_email(clean_email)
    if not email_is_valid:
        return False, email_message

    password_is_valid, password_message = validate_password(password)
    if not password_is_valid:
        return False, password_message

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT Reader_ID
            FROM readers
            WHERE Email = %s
            """,
            (clean_email,),
        )
        existing_reader = cursor.fetchone()

        if existing_reader:
            return False, "This email has already been registered."

        cursor.execute(
            """
            INSERT INTO readers (
                Name,
                Email,
                Password_Hash,
                Preferred_Category,
                Receive_Recommendations
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                name,
                clean_email,
                hash_password(password),
                preferred_category,
                receive_recommendations,
            ),
        )

        connection.commit()
        return True, "Registration successful."

    except Exception as exc:
        if connection:
            connection.rollback()
        return False, f"Registration failed: {exc}"

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def login_or_register_google_reader(user_info: dict) -> tuple[bool, str, dict | None]:
    google_sub = str(_claim(user_info, "sub") or "").strip()
    email = str(_claim(user_info, "email") or "").strip().lower()
    email_verified = _is_truthy(_claim(user_info, "email_verified"))

    if not google_sub:
        return False, "Google login did not provide an account ID.", None

    if not email_verified:
        return False, "Google email must be verified.", None

    email_is_valid, email_message = validate_google_email(email)
    if not email_is_valid:
        return False, email_message, None

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        _ensure_google_sub_column(cursor)

        cursor.execute(
            f"""
            SELECT {READER_SELECT_COLUMNS}
            FROM readers
            WHERE Google_Sub = %s
            """,
            (google_sub,),
        )
        reader = cursor.fetchone()

        if reader:
            return True, "Google login successful.", reader

        cursor.execute(
            f"""
            SELECT {READER_SELECT_COLUMNS}
            FROM readers
            WHERE Email = %s
            """,
            (email,),
        )
        reader = cursor.fetchone()

        if reader:
            if reader.get("Google_Sub"):
                return False, "This email is already linked to another Google account.", None

            cursor.execute(
                """
                UPDATE readers
                SET Google_Sub = %s
                WHERE Reader_ID = %s
                """,
                (google_sub, reader["Reader_ID"]),
            )
            connection.commit()
            reader["Google_Sub"] = google_sub
            return True, "Google login successful.", reader

        placeholder_password = secrets.token_urlsafe(32)
        cursor.execute(
            """
            INSERT INTO readers (
                Name,
                Email,
                Google_Sub,
                Password_Hash,
                Receive_Recommendations
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                _google_reader_name(user_info, email),
                email,
                google_sub,
                hash_password(placeholder_password),
                True,
            ),
        )
        connection.commit()

        cursor.execute(
            f"""
            SELECT {READER_SELECT_COLUMNS}
            FROM readers
            WHERE Google_Sub = %s
            """,
            (google_sub,),
        )
        reader = cursor.fetchone()

        return True, "Google account created.", reader

    except Exception as exc:
        if connection:
            connection.rollback()
        return False, f"Google login failed: {exc}", None

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def login_reader(email: str, password: str) -> tuple[bool, str] | tuple[bool, str, dict]:
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                Reader_ID,
                Name,
                Email,
                Password_Hash,
                Preferred_Category,
                Points,
                Receive_Recommendations,
                Show_Reading_History,
                Created_At
            FROM readers
            WHERE Email = %s
            """,
            (email,),
        )
        reader = cursor.fetchone()

        if not reader:
            return False, "Reader account not found."

        if verify_password(password, reader["Password_Hash"]):
            return True, "Login successful.", reader

        return False, "Incorrect password."

    except Exception as exc:
        return False, f"Login failed: {exc}"

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
