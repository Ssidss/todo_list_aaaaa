import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / 'todo.db'

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    );
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS tokens (
        user_id INTEGER NOT NULL,
        token TEXT PRIMARY KEY,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    );
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS memberships (
        user_id INTEGER NOT NULL,
        team_id INTEGER NOT NULL,
        role TEXT NOT NULL,
        PRIMARY KEY (user_id, team_id),
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(team_id) REFERENCES teams(id)
    );
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS lists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        FOREIGN KEY(team_id) REFERENCES teams(id)
    );
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        list_id INTEGER NOT NULL,
        description TEXT NOT NULL,
        completed INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY(list_id) REFERENCES lists(id)
    );
    ''')
    conn.commit()
    conn.close()
