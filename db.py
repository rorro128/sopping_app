# db.py
import sqlite3

def init_db():
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS shopping
                 (id INTEGER PRIMARY KEY, date TEXT, total TEXT, quantity TEXT)''')
    conn.commit()
    conn.close()

init_db()