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
from app.network_config import VALID_NETWORKS, is_valid_network

def list_transactions(db_path='instance/mempush.db', network=None, show_confirmed=True):
    """List all transactions from the database in a formatted table
    
    Args:
        db_path (str): Path to the database file
        network (str): Network to filter by (optional)
        show_confirmed (bool): If False, hide confirmed transactions from the list
    """
    try:
        # Initialize components
        db = Database(db_path)
        formatter = TransactionFormatter()
        
        # Get transactions
        if network:
            if not is_valid_network(network):
                print(f"Error: Invalid network '{network}'. Valid networks are: {VALID_NETWORKS}")
                return
            transactions = db.get_transactions_by_network(network)
        else:
            transactions = db.get_all_transactions()
        
        if not transactions:
            network_msg = f" for network '{network}'" if network else ""
            print(f"No transactions found in the database{network_msg}.")
            return
        
        # Filter out confirmed transactions if show_confirmed is False
        if not show_confirmed:
            transactions = [tx for tx in transactions if tx[1] not in ['confirmed', 'failed']]
            if not transactions:
                print("No pending transactions found.")
                return
        
        # Prepare data for tabulate
        headers = ['TXID', 'Network', 'Status', 'Push Attempts', 'Created At', 'Updated At']
        table_data = []
        
        for tx in transactions:
            txid, network_name, status, push_attempts, created_at, updated_at = tx
            table_data.append([
                formatter.format_txid(txid),
                network_name,
                formatter.format_status(status),
                push_attempts,
                created_at,
                updated_at,
            ])
        
        # Print the table
        network_msg = f" for network '{network}'" if network else ""
        print(f"\nTransaction List{network_msg}:")
        print(tabulate(table_data, headers=headers, tablefmt='grid'))
        print(f"\nTotal transactions: {len(transactions)}")
        
    except Exception as e:
        print(f"Error: {e}")

def update_transactions(db_path='instance/mempush.db', network=None, base_url='http://localhost:5000'):
    """Update all transactions
    
    Args:
        db_path (str): Path to the database file
        network (str): Network to filter by (optional)
        base_url (str): Base URL of the Flask application
    """
    try:
        # Initialize components
        db = Database(db_path)
        formatter = TransactionFormatter()
        
        # Get transactions
        if network:
            if not is_valid_network(network):
                print(f"Error: Invalid network '{network}'. Valid networks are: {VALID_NETWORKS}")
                return
            transactions = db.get_transactions_by_network(network)
        else:
            transactions = db.get_all_transactions()
        
        if not transactions:
            network_msg = f" for network '{network}'" if network else ""
            print(f"No transactions found in the database{network_msg}.")
            return
        
        for tx in transactions:
            txid, network_name, status, push_attempts, created_at, updated_at = tx
            if status not in ['confirmed', 'error']:
                try:
                    # Use network-specific endpoint
                    network_to_use = network_name if network_name else (network if network else 'mainchain')
                    response = requests.post(
                        f'{base_url}/{network_to_use}/transaction/{txid}/push',
                        headers={'Content-Type': 'application/json'}
                    )
                    response.raise_for_status()
                    print(f"Push request sent for {txid} ({network_name}): {response.status_code}")
                except requests.exceptions.RequestException as e:
                    print(f"Failed to push transaction {txid} ({network_name}): {e}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='List and update transactions')
    parser.add_argument('--hide-confirmed', action='store_true', 
                       help='Hide confirmed transactions from the list')
    parser.add_argument('--network', type=str, choices=VALID_NETWORKS,
                       help='Filter by network (mainchain, testnetv3, testnetv4, signet)')
    parser.add_argument('--base-url', type=str, default='http://localhost:5000',
                       help='Base URL of the Flask application (default: http://localhost:5000)')
    args = parser.parse_args()
    
    list_transactions(show_confirmed=not args.hide_confirmed, network=args.network)
    update_transactions(network=args.network, base_url=args.base_url)
