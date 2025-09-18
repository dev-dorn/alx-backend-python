import sqlite3
import functools

# ----------------------------
# Global query cache
# ----------------------------
query_cache = {}

# ----------------------------
# Decorator to open/close DB
# ----------------------------
def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect("users.db")  # open connection
        try:
            return func(conn, *args, **kwargs)
        finally:
            conn.close()  # always close connection
    return wrapper

# ----------------------------
# Cache Decorator
# ----------------------------
def cache_query(func):
    """
    Caches results of SQL queries to avoid redundant DB calls.
    Uses the query string as the cache key.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        query = kwargs.get("query") or (args[1] if len(args) > 1 else None)
        if query in query_cache:
            print(f"🟢 Returning cached result for query: {query}")
            return query_cache[query]
        else:
            print(f"⚡ Executing and caching result for query: {query}")
            result = func(*args, **kwargs)
            query_cache[query] = result
            return result
    return wrapper

# ----------------------------
# Function with cache
# ----------------------------
@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

# ----------------------------
# Run Test
# ----------------------------
if __name__ == "__main__":
    # First call -> goes to DB
    users = fetch_users_with_cache(query="SELECT * FROM users")
    print("\nUsers:", users)

    # Second call -> cached
    users_again = fetch_users_with_cache(query="SELECT * FROM users")
    print("\nUsers (from cache):", users_again)
