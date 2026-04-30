# Login / logout logic
# Webb's responsibility

import bcrypt  # For password hashing
from Backend.DB_Stuff.db_connect import get_connection


# 1. Hash password:
# Convert the user's plain-text password into a hashed password.
def hash_password(password: str) -> str:
    hashed_bytes = bcrypt.hashpw(
        password.encode("utf-8"),  # bcrypt requires bytes, not a Python string
        bcrypt.gensalt()           # Generate a salt so the same password can produce different hashes
    )
    return hashed_bytes.decode("utf-8")  # Convert bytes back to string for database storage


# 2. Verify password:
# checkpw() is used to compare a plain-text password with a hashed password.
def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"),       # Convert string to bytes
        password_hash.encode("utf-8")   # Convert stored hash string to bytes
    )


# 3. Register:
# Insert a new reader account into the database.
def register_user(
    name: str,
    email: str,
    password: str,
    preferred_category: str = None,
    receive_recommendations: bool = True
):
    # The bcrypt algorithm only handles passwords up to 72 bytes.
    if len(password.encode("utf-8")) > 72:
        return False, "Password is too long. Please use a password under 72 bytes."

    # Connect to the database before inserting data.
    connection = get_connection()
    if connection is None:
        return False, "Database connection failed."

    # A cursor is used to execute SQL commands.
    cursor = connection.cursor(dictionary=True)

    try:
        # 1. Check whether the email already exists.
        cursor.execute(
            """
            SELECT Reader_ID
            FROM readers
            WHERE Email = %s
            """,
            (email,)
        )
        existing_user = cursor.fetchone()

        if existing_user:
            return False, "This email has already been registered."

        # 2. Hash the password before storing it in the database.
        password_hash = hash_password(password)

        # 3. Insert the new reader into the readers table.
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
                password_hash,
                preferred_category,
                receive_recommendations
            )
        )

        connection.commit()
        return True, "Registration successful."

    except Exception as e:
        connection.rollback()
        return False, f"Registration failed: {e}"

    finally:
        cursor.close()
        connection.close()


# 4. Login:
# Check whether the input email and password are correct.
def login_user(email: str, password: str):
    # Connect to the database to retrieve reader account data.
    connection = get_connection()
    if connection is None:
        return False, "Database connection failed."

    cursor = connection.cursor(dictionary=True)

    try:
        # 1. Find the reader account by email.
        cursor.execute(
            """
            SELECT Reader_ID, Name, Email, Password_Hash, Preferred_Category, Points
            FROM readers
            WHERE Email = %s
            """,
            (email,)
        )
        user = cursor.fetchone()

        # Account does not exist.
        if not user:
            return False, "Account not found."

        # 2. Verify the password.
        if verify_password(password, user["Password_Hash"]):
            return True, "Login successful.", user

        return False, "Incorrect password."

    except Exception as e:
        return False, f"Login failed: {e}"

    finally:
        cursor.close()
        connection.close()