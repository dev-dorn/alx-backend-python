import sqlite3
import functools

# Decorator to open/close DB

def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect("users.db") #open DB connection
        try:
            return func(conn, *args, **kwargs)# pass connection
        finally:
            conn.close()# always close connection
        return wrapper
# Decorate to manage transaction
def transactional(func):
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            result = func(conn, *args, **kwargs)
            conn.commit() # commit successful
            return result
        except Exception as e:
            conn.rollback() # rollback error
            print(f"Transaction failed:{e}")
            raise
    return wrapper
@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?",
    (new_email, user_id)
    )
if __name__ == "__main__":
    update_user_email(user_id=1, new_email="Crawford_Cartwright@hotmail.com")
    print("User email updated successfully")