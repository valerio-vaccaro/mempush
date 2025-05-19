#!/usr/bin/env python3
import sys
import os
from tabulate import tabulate
import requests
import argparse

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.database import Database
from scripts.formatters import TransactionFormatter

def list_transactions(db_path='instance/mempush.db', show_confirmed=True):
    """List all transactions from the database in a formatted table
    
    Args:
        db_path (str): Path to the database file
        show_confirmed (bool): If False, hide confirmed transactions from the list
    """
    try:
        # Initialize components
        db = Database(db_path)
        formatter = TransactionFormatter()
        
        # Get transactions
        transactions = db.get_all_transactions()
        
        if not transactions:
            print("No transactions found in the database.")
            return
        
        # Filter out confirmed transactions if show_confirmed is False
        if not show_confirmed:
            transactions = [tx for tx in transactions if tx[1] not in ['confirmed', 'failed']]
            if not transactions:
                print("No pending transactions found.")
                return
        
        # Prepare data for tabulate
        headers = ['TXID', 'Status', 'Push Attempts', 'Created At', 'Updated At']
        table_data = []
        
        for tx in transactions:
            txid, status, push_attempts, created_at, updated_at = tx
            table_data.append([
                formatter.format_txid(txid),
                formatter.format_status(status),
                push_attempts,
                created_at,
                updated_at,
            ])
        
        # Print the table
        print("\nTransaction List:")
        print(tabulate(table_data, headers=headers, tablefmt='grid'))
        print(f"\nTotal transactions: {len(transactions)}")
        
    except Exception as e:
        print(f"Error: {e}")

def update_transactions(db_path='instance/mempush.db'):
    """Update all transactions"""
    try:
        # Initialize components
        db = Database(db_path)
        formatter = TransactionFormatter()
        
        # Get transactions
        transactions = db.get_all_transactions()
        
        if not transactions:
            print("No transactions found in the database.")
            return
        
        for tx in transactions:
            txid, status, push_attempts, created_at, updated_at = tx
            if status != 'confirmed':
                try:
                    response = requests.post(
                        f'http://localhost:3000/transaction/{txid}/push',
                        headers={'Content-Type': 'application/json'}
                    )
                    response.raise_for_status()
                    print(f"Push request sent for {txid}: {response.status_code}")
                except requests.exceptions.RequestException as e:
                    print(f"Failed to push transaction {txid}: {e}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='List and update transactions')
    parser.add_argument('--hide-confirmed', action='store_true', 
                       help='Hide confirmed transactions from the list')
    args = parser.parse_args()
    
    list_transactions(show_confirmed=not args.hide_confirmed)
    update_transactions()