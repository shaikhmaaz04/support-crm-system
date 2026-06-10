import sqlite3
import os
from datetime import datetime

# We'll store the database file in the root of our project
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "crm.db")

def get_db_connection():
    """Establishes and returns a database connection. Automatically enables foreign keys."""
    conn = sqlite3.connect(DB_PATH)
    # Configure SQLite to return rows as dictionaries for easier JSON conversion
    conn.row_factory = sqlite3.Row  
    # Enable foreign key support in SQLite
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Creates the necessary tables if they don't already exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Create TICKETS Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT UNIQUE NOT NULL,
            customer_name TEXT NOT NULL,
            customer_email TEXT NOT NULL,
            subject TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Open',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. Create NOTES Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT NOT NULL,
            note_text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ticket_id) REFERENCES tickets (ticket_id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

# Run this block to test the setup directly
if __name__ == "__main__":
    init_db()