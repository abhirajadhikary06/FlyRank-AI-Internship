import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()

DB_NAME = "items.db"
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT, desc TEXT)")
    conn.commit()
    conn.close()
init_db()

class Item(BaseModel):
    name: str
    desc: str

@app.post("/items/{item_id}")
def read_item(item_id: int):
    conn = get_db()
    item = conn.execute("SELECT * FROM items WHERE id = ?", (item_id)).fetchone()
    conn.close()
    if item is None:
        raise HTTPException(status_code=404, detail="Item Not Found")
    return dict(item)

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    conn = get_db()
    cursor = conn.execute("UPDATE items SET name = ?, desc = ? WHERE id = ?", (item.name, item.desc, item_id))
    conn.commit()
    rows_affected = cursor.rowcount()
    conn.close()

    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Item Not Found")
    return {"id": item_id, **item.model_dump()}

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    conn = get_db()
    cursor = conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    rows_affected = cursor.rowcount

    if rows_affected == 0:
        raise HTTPException(status=404, detail="Item Not Found")
    return {"message":"Item Deleted Successfully"}