import sqlite3

# Connect to database (creates users.db if it doesn't exist)
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
""")

# Insert some sample data
cursor.executemany("INSERT INTO users (name) VALUES (?)", [
    ("Alice",),
    ("Bob",),
    ("Charlie",)
])

conn.commit()
conn.close()

print("Database and sample users created successfully.")
