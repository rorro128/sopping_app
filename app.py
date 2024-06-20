# app.py (modificado)
from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

@app.route('/')
def calendar():
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tasks')
    tasks = c.fetchall()
    conn.close()
    return render_template('calendar.html', tasks=tasks)

if __name__ == '__main__':
    app.run(debug=True)