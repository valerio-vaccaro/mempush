import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_path='instance/mempush.db'):
        self.db_path = db_path

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def get_all_transactions(self):
        """Get all transactions from the database"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT txid, status, push_attempts, created_at, updated_at
                FROM "transaction"
                ORDER BY created_at DESC
            ''')
            return cursor.fetchall()
        finally:
            conn.close() 