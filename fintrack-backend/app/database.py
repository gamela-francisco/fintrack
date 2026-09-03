import psycopg
from psycopg.rows import dict_row


def get_db_connection():
    """
    Opens a connection to the PostgreSQL database server.
    """
    conn = psycopg.connect(
        dbname="fintrack",
        user="gamel",
        row_factory=dict_row
    )
    return conn

def init_db():
    """ Creates the transactions table if it doesn't exist yet."""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id SERIAL PRIMARY KEY,
                amount DECIMAL NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                date DATE NOT NULL
                );
            """)
