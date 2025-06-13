from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import hashlib
import sqlite3
import secrets

from .db import init_db, get_connection

app = FastAPI(title="Todo List API")
security = HTTPBearer()

init_db()

def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM tokens WHERE token=?", (token.credentials,))
    row = cur.fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return row[0]

@app.post("/users/register")
def register(username: str, password: str):
    pwd_hash = hashlib.sha256(password.encode()).hexdigest()
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, pwd_hash))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Username taken")
    user_id = cur.lastrowid
    conn.close()
    return {"id": user_id, "username": username}

@app.post("/users/login")
def login(username: str, password: str):
    pwd_hash = hashlib.sha256(password.encode()).hexdigest()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE username=? AND password_hash=?", (username, pwd_hash))
    row = cur.fetchone()
    if row is None:
        conn.close()
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user_id = row[0]
    token = secrets.token_hex(16)
    cur.execute("INSERT OR REPLACE INTO tokens (user_id, token) VALUES (?, ?)", (user_id, token))
    conn.commit()
    conn.close()
    return {"token": token}

@app.post("/teams")
def create_team(name: str, user_id: int = Depends(get_current_user)):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO teams (name) VALUES (?)", (name,))
    team_id = cur.lastrowid
    cur.execute("INSERT INTO memberships (user_id, team_id, role) VALUES (?, ?, 'principal')", (user_id, team_id))
    conn.commit()
    conn.close()
    return {"team_id": team_id, "name": name}

@app.get("/teams")
def list_teams(user_id: int = Depends(get_current_user)):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""SELECT t.id, t.name, m.role FROM teams t
                JOIN memberships m ON m.team_id=t.id
                WHERE m.user_id=?""", (user_id,))
    teams = [dict(row) for row in cur.fetchall()]
    conn.close()
    return teams

@app.post("/teams/{team_id}/lists")
def create_list(team_id: int, title: str, user_id: int = Depends(get_current_user)):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM memberships WHERE user_id=? AND team_id=?", (user_id, team_id))
    if cur.fetchone() is None:
        conn.close()
        raise HTTPException(status_code=403, detail="Not a member")
    cur.execute("INSERT INTO lists (team_id, title) VALUES (?, ?)", (team_id, title))
    list_id = cur.lastrowid
    conn.commit()
    conn.close()
    return {"list_id": list_id, "title": title}

@app.post("/lists/{list_id}/tasks")
def add_task(list_id: int, description: str, user_id: int = Depends(get_current_user)):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""SELECT 1 FROM lists l
                JOIN memberships m ON l.team_id=m.team_id
                WHERE l.id=? AND m.user_id=?""", (list_id, user_id))
    if cur.fetchone() is None:
        conn.close()
        raise HTTPException(status_code=403, detail="No access to list")
    cur.execute("INSERT INTO tasks (list_id, description) VALUES (?, ?)", (list_id, description))
    task_id = cur.lastrowid
    conn.commit()
    conn.close()
    return {"task_id": task_id, "description": description}

@app.get("/lists/{list_id}/tasks")
def get_tasks(list_id: int, user_id: int = Depends(get_current_user)):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""SELECT 1 FROM lists l JOIN memberships m ON l.team_id=m.team_id
                WHERE l.id=? AND m.user_id=?""", (list_id, user_id))
    if cur.fetchone() is None:
        conn.close()
        raise HTTPException(status_code=403, detail="No access to list")
    cur.execute("SELECT id, description, completed FROM tasks WHERE list_id=?", (list_id,))
    tasks = [dict(row) for row in cur.fetchall()]
    conn.close()
    return tasks
