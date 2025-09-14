# 0-stream_users.py
"""
stream_users(): generator that yields user rows (dict) one-by-one.

Usage:
    from seed import connect_to_prodev
    for row in stream_users():
        print(row)
"""

from seed import connect_to_prodev

def stream_users():
    """
    Connects to ALX_prodev and yields each row from user_data as a dict.
    Uses a single loop (requirement).
    """
    conn = connect_to_prodev()
    try:
        # MySQL: use dictionary cursor, sqlite returns rows that behave like dict via row_factory
        if hasattr(conn, "cursor") and getattr(conn, "cursor").__name__ == 'function':
            # avoid introspection oddities; we'll just create cursor accordingly
            pass

        # For mysql.connector
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT user_id, name, email, age FROM user_data")
            for row in cursor:
                yield row
        except Exception:
            # sqlite fallback
            cur = conn.cursor()
            cur.execute("SELECT user_id, name, email, age FROM user_data")
            colnames = [d[0] for d in cur.description]
            for r in cur.fetchall():
                yield dict(zip(colnames, r))
        finally:
            try:
                cursor.close()
            except Exception:
                pass
    finally:
        try:
            conn.close()
        except Exception:
            pass
