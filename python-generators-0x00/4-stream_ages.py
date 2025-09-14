# 4-stream_ages.py
"""
stream_user_ages(): yields ages one-by-one.
compute_average_age(): uses the generator and computes average without loading all rows.
"""

from seed import connect_to_prodev

def stream_user_ages():
    """
    Yields user ages one by one (as integers).
    """
    conn = connect_to_prodev()
    try:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT age FROM user_data")
            for row in cursor:
                yield int(row["age"])
        except Exception:
            cur = conn.cursor()
            cur.execute("SELECT age FROM user_data")
            for r in cur.fetchall():
                yield int(r[0])
    finally:
        try:
            conn.close()
        except Exception:
            pass


def compute_average_age():
    """
    Consume stream_user_ages() and compute average without loading all ages.
    Uses a single loop over generator.
    Prints: Average age of users: <average>
    """
    total = 0
    count = 0
    for age in stream_user_ages():
        total += age
        count += 1

    avg = (total / count) if count else 0
    print(f"Average age of users: {avg:.2f}")
    return avg


# If run directly, compute and print average
if __name__ == "__main__":
    compute_average_age()
