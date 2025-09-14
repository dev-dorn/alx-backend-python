#!/usr/bin/python3
"""
1-batch_processing.py

Functions:
- stream_users_in_batches(batch_size): generator yielding batches (list of rows).
- batch_processing(batch_size): processes each batch and prints users with age > 25.

Constraints:
- stream_users_in_batches → uses single loop (while True + LIMIT/OFFSET).
- batch_processing → uses up to 2 loops (outer over batches, inner over users).
"""

from seed import connect_to_prodev


def stream_users_in_batches(batch_size):
    """
    Generator that yields lists of rows (each row as dict) in batches.
    Uses LIMIT/OFFSET approach. Single loop (while True).
    """
    conn = connect_to_prodev()
    offset = 0
    try:
        while True:
            try:
                # Try MySQL-style query
                cursor = conn.cursor(dictionary=True)
                cursor.execute(
                    "SELECT user_id, name, email, age "
                    "FROM user_data ORDER BY user_id LIMIT %s OFFSET %s",
                    (batch_size, offset),
                )
                rows = cursor.fetchall()
            except Exception:
                # SQLite fallback (no dictionary=True, ? placeholders)
                cur = conn.cursor()
                cur.execute(
                    "SELECT user_id, name, email, age "
                    "FROM user_data ORDER BY user_id LIMIT ? OFFSET ?",
                    (batch_size, offset),
                )
                fetched = cur.fetchall()
                colnames = [d[0] for d in cur.description]
                rows = [dict(zip(colnames, r)) for r in fetched]

            if not rows:
                break

            yield rows  # ✅ generator, not return
            offset += batch_size
    finally:
        try:
            conn.close()
        except Exception:
            pass


def batch_processing(batch_size):
    """
    Process batches and print users older than 25.
    Uses only 2 loops (outer: batches, inner: users).
    """
    for batch in stream_users_in_batches(batch_size):
        for user in batch:
            try:
                age = int(user.get("age", 0))
            except Exception:
                age = 0
            if age > 25:
                print(user)
