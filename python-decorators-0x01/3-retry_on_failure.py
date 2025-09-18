import time
import sqlite3
import functools

#Decorator to open/close DB connection
def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect("users.db")
        try:
            return func(conn, *args, **kwargs)
        finally:
            conn.close()
    return wrapper

#retry decorator
def retry_on_failure(retries=3, delay=2):
    """
    Retries the wrapped function if it raises an exception.
    :param retries: number of retries
    :param delay: seconds to wait between retries
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    print(f"Attempt {attempt} failed: {e}")
                    if attempt < retries:
                        time.sleep(delay)
            print("All retry attempts failed.")
            raise last_exception
        return wrapper
    return decorator
# Function to fetch users
@with_db_connection
@retry_on_failure(retries=3, delay=2)
def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

# Run test

if __name__ == "__main__":
    try:
        users = fetch_users_with_retry()
        print("\n✅ Users fetched successfully:")
        for user in users:
            print(user)
    except Exception as e:
        print(f"\n❌ Failed after retries: {e}")