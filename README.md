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

- `POST /transaction/submit`
  ```json
  {
    "raw_tx": "hex_string"
  }
  ```
  Submit a new raw transaction to the system.

- `POST /transaction/<txid>/push`
  Push a transaction to the Bitcoin mempool.

- `POST /transaction/<txid>/delete`
  Delete a transaction from the database.

- `GET /transaction/<txid>`
  Get detailed information about a specific transaction.
