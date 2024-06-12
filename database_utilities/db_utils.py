import sqlite3
from datetime import datetime, timedelta

from database_utilities import SQLITE_DB_FILE
from database_utilities.queries import *


class DBConnection:
    connection = sqlite3.connect(SQLITE_DB_FILE, check_same_thread=False)
    cursor = connection.cursor()

    def __init__(self):
        table_exists = self.cursor.execute(CHECK_TABLE_EXISTS).fetchone()
        if not table_exists:
            self.cursor.execute(CREATE_TABLE_QUERY)
            self.cursor.execute(ENTRY_LOCK_TRIGGER)
            self.connection.commit()

    # Function to load the temporary entry if it exists
    def load_temp_entry(self):
        self.cursor.execute(LAST_TEMP_ENTRY_QUERY)
        result = self.cursor.fetchone()
        return result[5] if result else None

    def load_last_entry(self):
        self.cursor.execute(LAST_ENTRY_QUERY)
        result = self.cursor.fetchone()
        return result if result else None

    def is_new_day(self):
        self.cursor.execute(LATEST_DATE_ENTRY)
        latest_date_key = self.cursor.fetchone()
        if latest_date_key:
            latest_date_key = datetime.strptime(latest_date_key[0], '%Y-%m-%d').date()
            today = datetime.today().date()
            return today > latest_date_key
        return True

    def lock_latest_unlocked_entry(self):
        if self.is_new_day():
            yesterday = datetime.today().date() - timedelta(days=1)
            yesterday_str = yesterday.strftime('%Y-%m-%d')

            self.cursor.execute(GET_YESTERDAY_ENTRY, (yesterday_str,))

            entry_to_lock = self.cursor.fetchone()

            if entry_to_lock:
                # Lock the entry
                self.cursor.execute('''
                %s''' % LOCK_YESTERDAY_ENTRY, (yesterday_str,))

                self.connection.commit()

    def insert_new_entry(self, content: str, title=None, summary=None, sentiment=None):
        date_key = datetime.now().strftime('%Y-%m-%d')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        locked = 0
        if title is not None and summary is not None and sentiment is not None:
            locked = 1

        existing_content = self.load_temp_entry()

        if existing_content:
            content = existing_content + "\n" + content
        self.cursor.execute(INSERT_NEW_ENTRY, (date_key, timestamp, title, summary, sentiment, content, locked))
        self.connection.commit()

    def close_connection(self):
        try:
            self.connection.close()
        except Exception as exp:
            print(exp)
