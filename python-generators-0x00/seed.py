# seed.py
"""
Seed & DB helper for ALX_prodev user_data table.

Primary: MySQL using mysql-connector-python.
Fallback: sqlite3 (file: alx_prodev_fallback.db) if MySQL not available.

Environment variables (optional):
  MYSQL_HOST (default: localhost)
  MYSQL_PORT (default: 3306)
  MYSQL_USER (default: root)
  MYSQL_PASSWORD (default: empty)
"""

import os
import csv
import uuid
import logging

# Try to import mysql connector; if not available, we'll use sqlite3 fallback.
try:
    import mysql.connector
    from mysql.connector import errorcode
    HAS_MYSQL = True
except Exception:
    HAS_MYSQL = False

import sqlite3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed")

# Database connection defaults
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")

SQLITE_FILE = os.getenv("SQLITE_FILE", "alx_prodev_fallback.db")


def connect_db():
    """
    Connects to DB server (MySQL server if available); returns a connection object.
    For MySQL: connects without selecting a database (server connection).
    For sqlite fallback: returns sqlite3.Connection.
    """
    if HAS_MYSQL:
        try:
            conn = mysql.connector.connect(
                host=MYSQL_HOST,
                port=MYSQL_PORT,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                autocommit=True
            )
            logger.info("Connected to MySQL server.")
            return conn
        except Exception as e:
            logger.warning("MySQL connect failed: %s. Falling back to sqlite.", e)

    # Fallback to sqlite3
    conn = sqlite3.connect(SQLITE_FILE)
    conn.row_factory = sqlite3.Row
    logger.info("Using sqlite fallback database at %s", SQLITE_FILE)
    return conn


def create_database(connection):
    """
    Create database ALX_prodev if not exists (MySQL).
    If sqlite fallback, does nothing (sqlite uses file).
    """
    if HAS_MYSQL and isinstance(connection, mysql.connector.connection_cext.CMySQLConnection):
        cursor = connection.cursor()
        try:
            cursor.execute(
                "CREATE DATABASE IF NOT EXISTS ALX_prodev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
            )
            logger.info("Database ALX_prodev created or already exists.")
        finally:
            cursor.close()
    else:
        # sqlite: nothing to do
        logger.info("SQLite fallback - no CREATE DATABASE step.")


def connect_to_prodev():
    """
    Connect to the ALX_prodev database and return a connection object.
    Uses MySQL if available, otherwise uses sqlite file.
    """
    if HAS_MYSQL:
        try:
            conn = mysql.connector.connect(
                host=MYSQL_HOST,
                port=MYSQL_PORT,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database="ALX_prodev",
                autocommit=False
            )
            logger.info("Connected to ALX_prodev (MySQL).")
            return conn
        except mysql.connector.Error as err:
            logger.error("Could not connect to ALX_prodev: %s", err)
            raise
    else:
        conn = sqlite3.connect(SQLITE_FILE)
        conn.row_factory = sqlite3.Row
        logger.info("Connected to sqlite fallback DB.")
        return conn


def create_table(connection):
    """
    Create user_data table if not exists with fields:
      user_id (Primary Key, UUID stored as CHAR(36)), name, email, age
    """
    if HAS_MYSQL and isinstance(connection, mysql.connector.connection_cext.CMySQLConnection):
        cursor = connection.cursor()
        ddl = """
        CREATE TABLE IF NOT EXISTS user_data (
          user_id CHAR(36) NOT NULL PRIMARY KEY,
          name VARCHAR(255) NOT NULL,
          email VARCHAR(255) NOT NULL,
          age INT NOT NULL,
          INDEX idx_user_id (user_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        cursor.execute(ddl)
        connection.commit()
        cursor.close()
        logger.info("Table user_data created successfully (MySQL).")
    else:
        # sqlite3 create
        cursor = connection.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_data (
          user_id TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          email TEXT NOT NULL,
          age INTEGER NOT NULL
        );
        """)
        connection.commit()
        cursor.close()
        logger.info("Table user_data created successfully (SQLite).")


def insert_data(connection, csv_path):
    """
    Insert CSV rows into user_data.
    csv_path: path to CSV file with headers: user_id,name,email,age
    Avoid duplicates by using ON DUPLICATE KEY UPDATE (MySQL) or INSERT OR REPLACE (sqlite).
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(csv_path)

    rows_to_insert = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            # ensure keys exist
            uid = r.get("user_id") or r.get("id") or str(uuid.uuid4())
            name = r.get("name") or ""
            email = r.get("email") or ""
            age = int(float(r.get("age") or 0))
            rows_to_insert.append((uid, name, email, age))

    if HAS_MYSQL and isinstance(connection, mysql.connector.connection_cext.CMySQLConnection):
        cursor = connection.cursor()
        insert_sql = """
        INSERT INTO user_data (user_id, name, email, age)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
          name = VALUES(name),
          email = VALUES(email),
          age = VALUES(age);
        """
        try:
            # batch insert in chunks
            batch = 500
            for i in range(0, len(rows_to_insert), batch):
                chunk = rows_to_insert[i : i + batch]
                cursor.executemany(insert_sql, chunk)
                connection.commit()
            logger.info("Inserted/updated %d rows into user_data (MySQL).", len(rows_to_insert))
        finally:
            cursor.close()
    else:
        # sqlite fallback
        cursor = connection.cursor()
        insert_sql = "INSERT OR REPLACE INTO user_data (user_id, name, email, age) VALUES (?, ?, ?, ?);"
        try:
            cursor.executemany(insert_sql, rows_to_insert)
            connection.commit()
            logger.info("Inserted/updated %d rows into user_data (SQLite).", len(rows_to_insert))
        finally:
            cursor.close()
