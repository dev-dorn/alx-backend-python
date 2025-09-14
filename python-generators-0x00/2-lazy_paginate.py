# 2-lazy_paginate.py
"""
lazy_pagination(page_size): yields pages (list of rows).
Includes paginate_users(page_size, offset) helper.
Only one loop in lazy_pagination (while).
"""

from seed import connect_to_prodev

def paginate_users(page_size, offset):
    """
    Fetch a page of rows from DB and return list of dict rows.
    """
    conn = connect_to_prodev()
    try:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT user_id, name, email, age FROM user_data ORDER BY user_id LIMIT %s OFFSET %s", (page_size, offset))
            rows = cursor.fetchall()
            return rows
        except Exception:
            cur = conn.cursor()
            cur.execute("SELECT user_id, name, email, age FROM user_data ORDER BY user_id LIMIT ? OFFSET ?", (page_size, offset))
            fetched = cur.fetchall()
            colnames = [d[0] for d in cur.description]
            return [dict(zip(colnames, r)) for r in fetched]
    finally:
        try:
            conn.close()
        except Exception:
            pass


def lazy_pagination(page_size):
    """
    Generator that yields pages lazily. Single loop only.
    """
    offset = 0
    while True:
        page = paginate_users(page_size, offset)
        if not page:
            break
        yield page
        offset += page_size
