import _sqlite3

class DatabaseConnection:
    """ 
    a custom context manager to handle opening and closing of a Sqlite database connection
    """

    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None

    def __enter__(self):
        #open the connection when entering the context
        self.conn = _sqlite3.connect(self.db_name)
        return self.conn #this iis what "as" recieves
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # close the connection when exiting
        if self.conn:
            self.conn.close()
        # Returning False will propagate any exceptions
        return False

if __name__ == "__main__":
    with DatabaseConnection("users.db")as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
        print("Users:", results)
