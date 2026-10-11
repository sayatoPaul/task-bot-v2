from fastapi import FastAPI
import sqlite3

app = FastAPI()

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            task TEXT,
            done INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_db() # сам по себе при запуске

# endpoint 1 — GET /tasks (все задачи)
@app.get('/tasks')
def get_tasks(user_id: int):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM tasks WHERE user_id = ?', (user_id,))
    tasks = cursor.fetchall()

    conn.close()
    return tasks

# endpoint 2 — POST /tasks (создать)
@app.post('/tasks')
def create_task(task: str, user_id: int):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO tasks (user_id, task) VALUES (?, ?)', (user_id, task))

    conn.commit()
    conn.close()
    return {"status": "created", "task": task}


# endpoint 3 — POST /tasks{task_id} (изменить)
@app.put('/tasks/{task_id}')
def edit_task(task_id: int, user_id: int, done: int):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('UPDATE tasks SET done = ? WHERE id = ? AND user_id = ?', (done, task_id, user_id))

    conn.commit()
    conn.close()
    return {"status": "updated", "task_id": task_id}

# ENDPOINT №4 — DELETE /tasks/{task_id} (удалить)
@app.delete('/tasks/{task_id}')
def delete_task(task_id: int, user_id: int):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM tasks WHERE id = ? AND user_id = ?', (task_id,user_id))

    conn.commit()
    conn.close()
    return {"status": "deleted", "task_id": task_id}
