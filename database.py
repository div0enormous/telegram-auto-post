import sqlite3
import json

class Database:
    def __init__(self, db_name='bot_data.db'):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()

        # Posts table
        c.execute('''CREATE TABLE IF NOT EXISTS posts
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      title TEXT,
                      content TEXT,
                      media_type TEXT,
                      media_file_id TEXT,
                      buttons TEXT,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

        # Channels table
        c.execute('''CREATE TABLE IF NOT EXISTS channels
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      channel_id TEXT UNIQUE,
                      channel_name TEXT,
                      added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

        conn.commit()
        conn.close()

    def add_post(self, title, content, media_type, media_file_id, buttons):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("""INSERT INTO posts (title, content, media_type, media_file_id, buttons)
                     VALUES (?, ?, ?, ?, ?)""",
                 (title, content, media_type, media_file_id, json.dumps(buttons)))
        post_id = c.lastrowid
        conn.commit()
        conn.close()
        return post_id

    def update_post(self, post_id, title, content, media_type, media_file_id, buttons):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("""UPDATE posts SET title = ?, content = ?, media_type = ?, media_file_id = ?, buttons = ?
                     WHERE id = ?""",
                  (title, content, media_type, media_file_id, json.dumps(buttons), post_id))
        conn.commit()
        conn.close()

    def get_post(self, post_id):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("SELECT content, media_type, media_file_id, buttons FROM posts WHERE id = ?", (post_id,))
        post = c.fetchone()
        conn.close()
        return post

    def get_all_posts(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("SELECT id, title, created_at FROM posts ORDER BY created_at DESC")
        posts = c.fetchall()
        conn.close()
        return posts

    def delete_post(self, post_id):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        conn.commit()
        conn.close()

    def search_posts(self, query):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        # Using LOWER() for case-insensitive search
        c.execute("SELECT id, title FROM posts WHERE LOWER(title) LIKE LOWER(?) OR LOWER(content) LIKE LOWER(?) ORDER BY created_at DESC",
                  (f'%{query}%', f'%{query}%'))
        posts = c.fetchall()
        conn.close()
        return posts

    def add_channel(self, channel_id, channel_name):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO channels (channel_id, channel_name) VALUES (?, ?)",
                 (channel_id, channel_name))
        conn.commit()
        conn.close()

    def get_all_channels(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("SELECT channel_id, channel_name FROM channels")
        channels = c.fetchall()
        conn.close()
        return channels

    def remove_channel(self, channel_id):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("DELETE FROM channels WHERE channel_id = ?", (channel_id,))
        conn.commit()
        conn.close()
