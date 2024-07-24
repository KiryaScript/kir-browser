import sqlite3
from datetime import datetime

class BrowserHistory:
    def __init__(self, db_path='browser_history.db'):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS history
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         url TEXT NOT NULL,
         title TEXT,
         visit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
        ''')
        self.conn.commit()

    def add_visit(self, url, title):
        self.cursor.execute('INSERT INTO history (url, title) VALUES (?, ?)', (url, title))
        self.conn.commit()

    def get_history(self, limit=100):
        self.cursor.execute('SELECT url, title, visit_time FROM history ORDER BY visit_time DESC LIMIT ?', (limit,))
        return self.cursor.fetchall()

    def clear_history(self):
        self.cursor.execute('DELETE FROM history')
        self.conn.commit()

    def close(self):
        self.conn.close()