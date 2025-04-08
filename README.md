# Mempush

A lightweight Flask web application for managing and pushing Bitcoin transactions to the mempool. This tool provides a simple interface to submit raw transactions, track their status, and manually push them to the Bitcoin network.

## Features

- 🚀 Submit raw Bitcoin transactions
- 📊 Track transaction status (pending, confirmed, failed)
- 🔄 Manual transaction pushing to mempool
- 🗑️ Transaction deletion
- 👁️ Toggle visibility of confirmed transactions
- 📝 Transaction history management
- ⚡ Real-time status updates

## Quick Start

1. **Clone the repository**

```bash
git clone https://github.com/valerio-vaccaro/mempush.git
cd mempush
```

2. **Set up virtual environment**

```bash
python -m venv venv
source venv/bin/activate
```


3. **Install dependencies**

```bash
pip install -r requirements.txt
```


5. **Run the application**

```bash
flask run
```

6. **Call script**
Seup a cron job to push transactions to the mempool (daily) or do manually.

```bash
python scripts/push_transactions.py --hide-confirmed
```


6. **Access the web interface**
Open your browser and navigate to `http://localhost:5000`


## API Endpoints

### Transaction Management

- `GET /`
  - Returns the main index page

- `GET /transactions`
  - Returns a list of all transactions ordered by creation date (newest first)

- `GET /transaction/<txid>`
  - Returns detailed information about a specific transaction
  - Returns 404 if transaction not found

- `POST /transaction/submit`
  ```json
  {
    "raw_tx": "hex_string",
    "txid": "optional_txid"  // If provided, will verify against calculated txid
  }
  ```
  - Submit a new raw transaction to the system
  - Validates hex format and transaction structure
  - Returns 400 for invalid transactions
  - Returns 201 with transaction details on success

- `POST /transaction/<txid>/push`
  - Pushes a transaction to the Bitcoin mempool
  - Checks if transaction is already confirmed
  - Updates transaction status (success/failed/confirmed)
  - Returns transaction status and analysis result
  - Returns 404 if transaction not found

- `POST /transaction/<txid>/delete`
  - Deletes a confirmed transaction from the database
  - Only allows deletion of confirmed transactions
  - Returns 403 if transaction is not confirmed
  - Returns 404 if transaction not found

### Response Status Codes
- 200: Success
- 201: Created
- 400: Bad Request (invalid input)
- 403: Forbidden (unauthorized action)
- 404: Not Found
- 500: Server Error

## Data Model

### Transaction
The Transaction model represents a Bitcoin transaction in the system with the following fields:

- `id` (Integer): Primary key
- `raw_tx` (Text): Raw transaction hex string
- `txid` (String[64]): Unique transaction ID
- `status` (String[20]): Transaction status (default: 'pending')
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp
- `push_attempts` (Integer): Number of push attempts (default: 0)
- `analysis_result` (Text): Result of transaction analysis

### Transaction Status
Possible transaction statuses:
- `pending`: Initial state
- `success`: Successfully pushed to mempool
- `failed`: Failed to push to mempool
- `confirmed`: Transaction is confirmed in blockchain
- `error`: Error occurred during processing
