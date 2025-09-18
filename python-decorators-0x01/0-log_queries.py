#!/usr/bin/env python3
import sqlite3
import functools
from datetime import datetime   # ✅ required

# -------------------------
# Decorator to log queries
# -------------------------
def log_queries(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        query = None
        if 'query' in kwargs:
            query = kwargs['query']
        elif args:
            query = args[0]

        if query:
            print(f"[{datetime.now()}] Executing SQL query: {query}")
        else:
            print(f"[{datetime.now()}] No SQL query found to log")

        return func(*args, **kwargs)
    return wrapper


# -------------------------
# Initialize database
# -------------------------
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Create the correct users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL
    )
    """)

    # Insert sample users only if table is empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            [
                ("Alice", "alice@example.com"),
                ("Bob", "bob@example.com"),
                ("Charlie", "charlie@example.com")
            ]
        )
        print("✅ Users inserted into database")
    else:
        print("ℹ️ Users already exist")

    conn.commit()
    conn.close()


# -------------------------
# Query function with decorator
# -------------------------
@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results


# -------------------------
# Run everything
# -------------------------
if __name__ == "__main__":
    init_db()  # make sure table and data exist

    users = fetch_all_users(query="SELECT * FROM users")
    print("\nFetched Users:")
    for user in users:
        print(user)
