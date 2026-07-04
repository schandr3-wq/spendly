import sqlite3
from datetime import date
from pathlib import Path

from werkzeug.security import generate_password_hash

# Database lives in the project root, regardless of the working directory
DB_PATH = Path(__file__).resolve().parent.parent / "spendly.db"

# Fixed list of expense categories used across the app
CATEGORIES = [
    "Food",
    "Transport",
    "Bills",
    "Health",
    "Entertainment",
    "Shopping",
    "Other",
]


def get_db():
    """Return a SQLite connection with dict-like rows and FK enforcement."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables. Safe to call multiple times."""
    conn = get_db()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT NOT NULL,
                email         TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at    TEXT DEFAULT (datetime('now'))
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL REFERENCES users(id),
                amount      REAL NOT NULL,
                category    TEXT NOT NULL,
                date        TEXT NOT NULL,
                description TEXT,
                created_at  TEXT DEFAULT (datetime('now'))
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def create_user(name, email, password):
    """Hash the password and insert a new user. Returns the new user's id.

    Raises sqlite3.IntegrityError if the email is already taken.
    """
    conn = get_db()
    try:
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, generate_password_hash(password)),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_user_by_email(email):
    """Return the user row for the given email, or None if not found."""
    conn = get_db()
    try:
        return conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
    finally:
        conn.close()


def get_user_by_id(user_id):
    """Return the user row for the given id, or None if not found."""
    conn = get_db()
    try:
        return conn.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    finally:
        conn.close()


def update_user(user_id, name, email):
    """Update a user's name and email.

    Raises sqlite3.IntegrityError if the email is taken by another user.
    """
    conn = get_db()
    try:
        conn.execute(
            "UPDATE users SET name = ?, email = ? WHERE id = ?",
            (name, email, user_id),
        )
        conn.commit()
    finally:
        conn.close()


def update_user_password(user_id, password):
    """Hash the password and store it for the given user."""
    conn = get_db()
    try:
        conn.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (generate_password_hash(password), user_id),
        )
        conn.commit()
    finally:
        conn.close()


def seed_db():
    """Insert a demo user and sample expenses. Runs only on an empty database."""
    conn = get_db()
    try:
        count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if count > 0:
            return

        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", generate_password_hash("demo123")),
        )
        user_id = cursor.lastrowid

        today = date.today()

        def day(d):
            return today.replace(day=d).isoformat()

        sample_expenses = [
            (42.50, "Food", day(1), "Groceries for the week"),
            (15.00, "Transport", day(4), "Metro card top-up"),
            (120.00, "Bills", day(8), "Electricity bill"),
            (35.75, "Health", day(12), "Pharmacy"),
            (28.00, "Entertainment", day(15), "Movie night"),
            (89.99, "Shopping", day(19), "New running shoes"),
            (12.30, "Other", day(23), None),
            (18.40, "Food", day(27), "Dinner out"),
        ]
        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) "
            "VALUES (?, ?, ?, ?, ?)",
            [(user_id, amount, category, expense_date, description)
             for amount, category, expense_date, description in sample_expenses],
        )
        conn.commit()
    finally:
        conn.close()
