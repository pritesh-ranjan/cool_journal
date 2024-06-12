CREATE_TABLE_QUERY = '''
            CREATE TABLE IF NOT EXISTS entries (
                date_key VARCHAR(10) PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                Title TEXT,
                Summary TEXT,
                Sentiment TEXT,
                content TEXT NOT NULL,
                locked BOOLEAN NOT NULL DEFAULT 0
                CONSTRAINT check_locked_content CHECK (
                    (locked = 0) OR 
                    (locked = 1 AND Title IS NOT NULL AND Summary IS NOT NULL AND Sentiment IS NOT NULL)
                )
            )
        '''

ENTRY_LOCK_TRIGGER = '''CREATE TRIGGER prevent_update_when_locked
                BEFORE UPDATE ON entries
                FOR EACH ROW
                WHEN OLD.locked = 1
                BEGIN
                    SELECT RAISE(ABORT, 'Record is locked and cannot be edited');
                END;'''

LAST_TEMP_ENTRY_QUERY = '''
                SELECT * FROM entries 
                WHERE locked = 0 
                ORDER BY timestamp DESC 
                LIMIT 1
        '''

LAST_ENTRY_QUERY = '''
             SELECT * FROM entries 
            ORDER BY timestamp DESC 
            LIMIT 1
        '''

LOCK_YESTERDAY_ENTRY = '''UPDATE entries
                SET locked = 1
                WHERE date_key = ?
                '''

GET_YESTERDAY_ENTRY = '''
            SELECT * FROM entries 
            WHERE date_key = ? AND locked = 0 
            ORDER BY timestamp DESC 
            LIMIT 1
            '''

LATEST_DATE_ENTRY = '''
        SELECT date_key FROM entries
        ORDER BY timestamp DESC 
        LIMIT 1
        '''

CHECK_TABLE_EXISTS = "SELECT name FROM sqlite_master WHERE type='table' AND name='entries'"

INSERT_NEW_ENTRY = '''
        INSERT OR REPLACE INTO entries (date_key, timestamp, Title, Summary, Sentiment, content, locked)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
