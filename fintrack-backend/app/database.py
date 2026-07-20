import sqlite3

DB_FILE = "fintrack.db"

def get_db_connection():
    """
    Opens a connection to the SQLite database file.
    """
    conn = sqlite3.connect(DB_FILE)
    # This setting tells sqlite3 to return rows as dictionaries
    # instead of tuples, making it much easier to convert to JSON later
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """ Creates the transactions table if it doesn't exist yet."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL NOT NULL,
        description TEXT NOT NULL,
        category TEXT NOT NULL,
        date TEXT NOT NULL
        );
    """)


    # Commit save the changes permanently to the file
    conn.commit()
    conn.close()