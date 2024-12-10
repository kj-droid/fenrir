
import sqlite3
import logging

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.logger = logging.getLogger("DatabaseManager")

    def execute_query(self, query, params=None):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                conn.commit()
                return cursor.fetchall()
        except Exception as e:
            self.logger.error(f"Database query failed: {str(e)}")
            return None
