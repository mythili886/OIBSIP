
import hashlib
import hmac
import secrets
import sqlite3

from database import get_connection


def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        200_000
    ).hex()

    return password_hash, salt


def register_user(username, password):
    username = username.strip()

    if len(username) < 3 or len(username) > 20:
        return False, "Username must be 3–20 characters."

    if not username.replace("_", "").isalnum():
        return False, "Use only letters, numbers and underscores."

    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    password_hash, salt = hash_password(password)

    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO users (username, password_hash, salt)
                VALUES (?, ?, ?)
                """,
                (username, password_hash, salt)
            )

        return True, "Registration successful!"

    except sqlite3.IntegrityError:
        return False, "Username already exists."


def login_user(username, password):
    with get_connection() as connection:
        user = connection.execute(
            """
            SELECT id, username, password_hash, salt
            FROM users
            WHERE username = ?
            """,
            (username.strip(),)
        ).fetchone()

    if user is None:
        return False, "Invalid username or password."

    entered_hash, _ = hash_password(password, user["salt"])

    if hmac.compare_digest(entered_hash, user["password_hash"]):
        return True, {
            "id": user["id"],
            "username": user["username"]
        }

    return False, "Invalid username or password."