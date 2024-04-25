import sqlite3
from datetime import datetime


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        self.create_table_users()
        self.create_table_user_actions()
        self.create_table_subscribers()
        self.create_table_news()


    def create_table_users(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                chat_id INTEGER UNIQUE,
                default_source TEXT,
                news_count INTEGER DEFAULT 5
            )
        ''')
        self.connection.commit()

    def create_table_user_actions(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_actions (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                action TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.connection.commit()

    def create_table_subscribers(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscribers (
                id INTEGER PRIMARY KEY,
                chat_id INTEGER UNIQUE
            )
        ''')
        self.connection.commit()

    def create_table_news(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY,
                title TEXT,
                link TEXT UNIQUE,
                time_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.connection.commit()

    def add_news(self, title, link):
        try:
            self.cursor.execute('INSERT INTO news (title, link, time_added) VALUES (?, ?, ?)',
                                (title, link, datetime.now()))
            self.connection.commit()
        except sqlite3.IntegrityError:
            print(f"News item with title '{title}' already exists in the database.")

    def get_latest_news(self):
        self.cursor.execute('SELECT * FROM news ORDER BY time_added DESC LIMIT 1')
        return self.cursor.fetchone()

    def has_new_news(self, title, link):
        self.cursor.execute('SELECT 1 FROM news WHERE title = ? AND link = ?', (title, link))
        return self.cursor.fetchone() is None

    def add_subscriber(self, chat_id):
        self.cursor.execute('INSERT INTO subscribers (chat_id) VALUES (?)', (chat_id,))
        self.connection.commit()

    def remove_subscriber(self, chat_id):
        self.cursor.execute('DELETE FROM subscribers WHERE chat_id = ?', (chat_id,))
        self.connection.commit()

    def is_subscriber(self, chat_id):
        self.cursor.execute('SELECT 1 FROM subscribers WHERE chat_id = ?', (chat_id,))
        return self.cursor.fetchone() is not None

    def get_all_subscribers(self):
        self.cursor.execute('SELECT chat_id FROM subscribers')
        return [row[0] for row in self.cursor.fetchall()]

    def get_user_default_source(self, chat_id):
        self.cursor.execute('SELECT default_source FROM users WHERE chat_id = ?', (chat_id,))
        row = self.cursor.fetchone()
        return row[0] if row else None

    def set_user_default_source(self, chat_id, default_source):
        self.cursor.execute('SELECT * FROM users WHERE chat_id = ?', (chat_id,))
        existing_record = self.cursor.fetchone()
        if existing_record:
            self.cursor.execute('UPDATE users SET default_source = ? WHERE chat_id = ?', (default_source, chat_id))
        else:
            self.cursor.execute('INSERT INTO users (chat_id, default_source) VALUES (?, ?)', (chat_id, default_source))
        self.connection.commit()

    def set_initial_news(self, initial_news):
        for news_item in initial_news:
            if not self.news_exists(news_item['title']):
                try:
                    self.cursor.execute('INSERT INTO news (title, link) VALUES (?, ?)',
                                        (news_item['title'], news_item['link']))
                except sqlite3.IntegrityError:
                    print(f"News item with title '{news_item['title']}' already exists in the database.")
        self.connection.commit()

    def news_exists(self, title):
        self.cursor.execute('SELECT 1 FROM news WHERE title = ?', (title,))
        return self.cursor.fetchone() is not None

    def get_user_news_count(self, chat_id):
        self.cursor.execute('SELECT news_count FROM users WHERE chat_id = ?', (chat_id,))
        row = self.cursor.fetchone()
        return row[0] if row else None

    def set_user_news_count(self, chat_id, news_count):
        self.cursor.execute('SELECT * FROM users WHERE chat_id = ?', (chat_id,))
        existing_record = self.cursor.fetchone()
        if existing_record:
            self.cursor.execute('UPDATE users SET news_count = ? WHERE chat_id = ?', (news_count, chat_id))
        else:
            self.cursor.execute('INSERT INTO users (chat_id, news_count) VALUES (?, ?)', (chat_id, news_count))
        self.connection.commit()

    def log_user_action(self, user_id, action):
        self.cursor.execute('INSERT INTO user_actions (user_id, action) VALUES (?, ?)', (user_id, action))
        self.connection.commit()

    def close(self):
        self.connection.close()
