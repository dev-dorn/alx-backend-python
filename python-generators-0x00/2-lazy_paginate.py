#!/usr/bin/python3
import seed  # import your DB connection functions from seed.py


def paginate_users(page_size, offset):
    """
    Fetch a single page of users from the database using LIMIT + OFFSET
    """
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return rows


def lazy_paginate(page_size):
    """
    Generator that lazily fetches users page by page.
    Only fetches the next page when requested.
    """
    offset = 0
    while True:
        rows = paginate_users(page_size, offset)
        if not rows:  # stop when no more rows
            break
        yield rows
        offset += page_size
