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
            # Check if network column exists
            try:
                cursor.execute('''
                    SELECT txid, network, status, push_attempts, created_at, updated_at
                    FROM "transaction"
                    ORDER BY created_at DESC
                ''')
            except sqlite3.OperationalError:
                # Fallback for old schema without network column
                cursor.execute('''
                    SELECT txid, status, push_attempts, created_at, updated_at
                    FROM "transaction"
                    ORDER BY created_at DESC
                ''')
                # Add 'mainchain' as default network for old records
                results = cursor.fetchall()
                return [(tx[0], 'mainchain', tx[1], tx[2], tx[3], tx[4]) for tx in results]
            return cursor.fetchall()
        finally:
            conn.close()

    def get_transactions_by_network(self, network):
        """Get transactions for a specific network"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            # Check if network column exists
            try:
                cursor.execute('''
                    SELECT txid, network, status, push_attempts, created_at, updated_at
                    FROM "transaction"
                    WHERE network = ?
                    ORDER BY created_at DESC
                ''', (network,))
            except sqlite3.OperationalError:
                # Fallback for old schema without network column
                if network == 'mainchain':
                    cursor.execute('''
                        SELECT txid, status, push_attempts, created_at, updated_at
                        FROM "transaction"
                        ORDER BY created_at DESC
                    ''')
                    results = cursor.fetchall()
                    return [(tx[0], 'mainchain', tx[1], tx[2], tx[3], tx[4]) for tx in results]
                else:
                    return []
            return cursor.fetchall()
        finally:
            conn.close() 