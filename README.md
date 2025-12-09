# 🚀 Mempush

A lightweight Flask web application for managing and pushing Bitcoin transactions to the mempool. This tool provides a simple interface to submit raw transactions, track their status, and manually push them to the Bitcoin network.

## ✨ Features

- 🚀 **Submit raw Bitcoin transactions** - Upload transaction hex data directly
- 📊 **Track transaction status** - Monitor pending, confirmed, and failed transactions
- 🔄 **Manual transaction pushing** - Push transactions to mempool with one click
- 🗑️ **Transaction deletion** - Clean up confirmed transactions from database
- 👁️ **Toggle visibility** - Show/hide confirmed transactions in the interface
- 📝 **Transaction history** - Complete audit trail of all transaction activities
- ⚡ **Real-time updates** - Live status updates and mempool integration
- 🔗 **RESTful API** - Full API access for programmatic transaction management
- 🌐 **Multi-network support** - Support for mainchain, testnetv3, testnetv4, and signet networks

## 🚀 Quick Start

### 1. 📥 Clone the repository

```bash
git clone https://github.com/valerio-vaccaro/mempush.git
cd mempush
```

### 2. 🐍 Set up virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

### 3. 📦 Install dependencies

```bash
pip install -r requirements.txt
```

### 4. 🗄️ Initialize database

**Note:** Database migrations run automatically when the application starts. You don't need to run `flask db upgrade` manually, but you can if you prefer.

If you're upgrading from an older version, the migration will automatically add the `network` column to existing transactions (defaulting to `mainchain`). The same transaction ID can now exist on different networks.

**Manual migration (optional):**
```bash
flask db upgrade
```

### 5. 🏃‍♂️ Run the application

```bash
flask run
```

### 6. 🔄 Set up automated pushing (Optional)

Set up a cron job to push transactions to the mempool daily or run manually:

```bash
# Push all transactions for all networks
python scripts/push_transactions.py --hide-confirmed

# Push transactions for a specific network
python scripts/push_transactions.py --network mainchain --hide-confirmed
python scripts/push_transactions.py --network testnetv3 --hide-confirmed
python scripts/push_transactions.py --network testnetv4 --hide-confirmed
python scripts/push_transactions.py --network signet --hide-confirmed
```

### 7. 🌐 Access the web interface

Open your browser and navigate to `http://localhost:5000`. The root URL will redirect to `/mainchain/`.

**Supported Networks:**
- **Mainchain**: `http://localhost:5000/mainchain/`
- **Testnet v3**: `http://localhost:5000/testnetv3/`
- **Testnet v4**: `http://localhost:5000/testnetv4/`
- **Signet**: `http://localhost:5000/signet/`

You can switch between networks using the dropdown menu in the navigation bar.

## 🔌 API Endpoints

All endpoints are network-specific. Replace `<network>` with one of: `mainchain`, `testnetv3`, `testnetv4`, or `signet`.

### 📋 Transaction Management

#### 🌐 Web Interface
- `GET /` - Redirects to `/mainchain/`
- `GET /<network>/` - Returns the main index page with transaction dashboard for the specified network
- `GET /<network>/transactions` - Returns a list of all transactions for the specified network ordered by creation date (newest first)
- `GET /<network>/transaction/<txid>` - Returns detailed information about a specific transaction for the specified network
- `GET /<network>/about` - Returns the about page

#### 🔌 REST API
- `GET /<network>/api/transactions` - **List all transactions** - Returns JSON array of all transactions for the specified network
- `GET /<network>/api/transaction/<txid>` - **Get transaction details** - Returns complete transaction information for the specified network
- `POST /<network>/api/transaction` - **Post transaction by txid** - Submit a txid to fetch and store transaction for the specified network
- `POST /<network>/api/transaction/push` - **Push raw transaction** - Submit hex transaction and push to mempool for the specified network
- `POST /<network>/transaction/<txid>/push` - **Push existing transaction** - Push an existing transaction to mempool
- `POST /<network>/transaction/<txid>/delete` - **Delete transaction** - Delete a confirmed or failed transaction

#### 📝 API Request Examples

**Submit a transaction by txid (mainchain):**
```bash
curl -X POST http://localhost:5000/mainchain/api/transaction \
  -H "Content-Type: application/json" \
  -d '{"txid": "abc123..."}'
```

**Push a raw transaction (testnetv3):**
```bash
curl -X POST http://localhost:5000/testnetv3/api/transaction/push \
  -H "Content-Type: application/json" \
  -d '{"raw_tx": "0100000001..."}'
```

**Get all transactions for a network:**
```bash
# Mainchain
curl -X GET http://localhost:5000/mainchain/api/transactions

# Testnet v3
curl -X GET http://localhost:5000/testnetv3/api/transactions

# Testnet v4
curl -X GET http://localhost:5000/testnetv4/api/transactions

# Signet
curl -X GET http://localhost:5000/signet/api/transactions
```

**Get specific transaction:**
```bash
curl -X GET http://localhost:5000/mainchain/api/transaction/abc123...
```

**Push existing transaction:**
```bash
curl -X POST http://localhost:5000/mainchain/transaction/abc123.../push
```

## 🗄️ Data Model

### 📋 Transaction
The Transaction model represents a Bitcoin transaction in the system with the following fields:

- 🔢 `id` (Integer): Primary key identifier
- 📄 `raw_tx` (Text): Raw transaction hex string
- 🆔 `txid` (String[64]): Transaction ID (SHA256 hash)
- 🌐 `network` (String[20]): Network identifier (mainchain, testnetv3, testnetv4, signet)
- 📊 `status` (String[20]): Transaction status (default: 'pending')
- 📅 `created_at` (DateTime): Creation timestamp
- 🔄 `updated_at` (DateTime): Last update timestamp
- 🔢 `push_attempts` (Integer): Number of push attempts (default: 0)
- 📝 `analysis_result` (Text): Result of transaction analysis

**Note:** The combination of `txid` and `network` is unique, allowing the same transaction to exist on different networks.

### 📈 Transaction Status
Possible transaction statuses:
- ⏳ `pending`: Initial state - transaction added but not pushed
- ✅ `success`: Successfully pushed to mempool
- ❌ `failed`: Failed to push to mempool
- 🔒 `confirmed`: Transaction is confirmed in blockchain
- 💥 `error`: Error occurred during processing

## 🛠️ Technical Details

### 🔧 Dependencies
- **Flask**: Web framework for the application
- **SQLAlchemy**: Database ORM for transaction storage
- **bitcoinlib**: Bitcoin transaction parsing and validation
- **requests**: HTTP client for mempool API integration

### 🌐 External Services
- **mempool.space**: Primary mempool service for transaction pushing, status checking, and blockchain exploration
  - Mainchain: `https://mempool.space/`
  - Testnet v3: `https://mempool.space/testnet/`
  - Testnet v4: `https://mempool.space/testnet4/`
  - Signet: `https://mempool.space/signet/`

## 📝 License

This project is open source and available under the MIT License.
