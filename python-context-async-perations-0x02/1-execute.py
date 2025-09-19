import sqlite3

class ExecuteQuery:
    """
    Context manager that takes a query and parameters, executes it automatically, and returns the results
    """
    
    def __init__(self, db_name, query, params=None):
        self.db_name = db_name
        self.query =query
        self.params = params if params else ()
        self.conn = None
        self.cursor= None
        self.results = None

    def __enter__(self):
        #Open Db connection and cursor
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

        #EXecute the query

        self.cursor.execute(self.query, self.params)
        self.results = self.cursor.fetchall()
        # Return the results
        return self.results

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Close cursor and connection
        if self.conn:
            self.conn.close()

        return False # dont suppress exceptions
    
if __name__ == "__main__":
    query ="SELECT * FROM users WHERE age > ?"
    params = (25,)

    with ExecuteQuery("users.db",query, params) as results:
        print("Users older than 25:", results)