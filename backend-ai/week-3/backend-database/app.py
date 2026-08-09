import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()

DB_NAME = "tasks.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            title TEXT NOT NULL, 
            description TEXT NOT NULL
        )
    """)
    
    # Check if empty
    existing_tasks = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    
    if existing_tasks == 0:
        sample_tasks = [
            ("Finish Internship Report", "Complete the week-3 backend task."),
            ("Learn FastAPI", "Read documentation on Pydantic models."),
            ("Database Backup", "Perform a full system backup.")
        ]
        conn.executemany("INSERT INTO tasks (title, description) VALUES (?, ?)", sample_tasks)
    conn.commit()
    conn.close()

init_db()

class Task(BaseModel):
    title: str
    description: str

@app.post("/tasks")
def create_task(task: Task):
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO tasks (title, description) VALUES (?, ?)", 
        (task.title, task.description)
    )
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return {"id": task_id, **task.model_dump()}

@app.get("/tasks")
def get_all_tasks():
    conn = get_db()
    tasks = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    return [dict(task) for task in tasks]

@app.get("/tasks/{task_id}")
def read_task(task_id: int):
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    if task is None:
        raise HTTPException(status_code=404, detail="Task Not Found")
    return dict(task)

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: Task):
    conn = get_db()
    cursor = conn.execute(
        "UPDATE tasks SET title = ?, description = ? WHERE id = ?", 
        (task.title, task.description, task_id)
    )
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()

    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Task Not Found")
    return {"id": task_id, **task.model_dump()}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    conn = get_db()
    cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()

    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Task Not Found")
    return {"message": "Task Deleted Successfully"}

@app.get("/task/{task_title}")
def search_task(task_title: str):
    conn = get_db()
    cursor = conn.execute("SELECT * FROM tasks WHERE title LIKE ?", (f"%{task_title}%",))
    tasks = cursor.fetchall()
    conn.commit()
    conn.close()

    if not tasks:
        raise HTTPException(status_code=404, detail="Task Not Found")
    return [dict(task) for task in tasks]