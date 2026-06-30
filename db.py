import sqlite3

def get_connection():
    conn = sqlite3.connect("progression.db")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def create_tables(conn):
    cursor = conn.cursor()
    with open("schema.sql", "r") as f:
        contents = f.read()
    cursor.executescript(contents)
    conn.commit()

if __name__ == "__main__":
    conn = get_connection()
    create_tables(conn)
    conn.close()
    print("Database created.")