# Login, registration, and password helpers for readers.

import bcrypt

from Backend.DB_Stuff.db_connect import get_connection


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


def register_reader(
    name: str,
    email: str,
    password: str,
    preferred_category: str | None = None,
    receive_recommendations: bool = True,
) -> tuple[bool, str]:
    if len(password.encode("utf-8")) > 72:
        return False, "Password is too long. Please use a password under 72 bytes."

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
            (email,),
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
                email,
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
