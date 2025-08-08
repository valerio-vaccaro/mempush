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
python scripts/push_transactions.py --hide-confirmed
```

### 7. 🌐 Access the web interface

Open your browser and navigate to `http://localhost:5000`

## 🔌 API Endpoints

### 📋 Transaction Management

#### 🌐 Web Interface
- `GET /` - Returns the main index page with transaction dashboard
- `GET /transactions` - Returns a list of all transactions ordered by creation date (newest first)
- `GET /transaction/<txid>` - Returns detailed information about a specific transaction

#### 🔌 REST API
- `GET /api/transactions` - **List all transactions** - Returns JSON array of all known transactions
- `GET /api/transaction/<txid>` - **Get transaction details** - Returns complete transaction information
- `POST /api/transaction` - **Post transaction by txid** - Submit a txid to fetch and store transaction
- `POST /api/transaction/push` - **Push raw transaction** - Submit hex transaction and push to mempool

#### 📝 API Request Examples

**Submit a transaction by txid:**
```bash
curl -X POST http://localhost:5000/api/transaction \
  -H "Content-Type: application/json" \
  -d '{"txid": "abc123..."}'
```

**Push a raw transaction:**
```bash
curl -X POST http://localhost:5000/api/transaction/push \
  -H "Content-Type: application/json" \
  -d '{"raw_tx": "0100000001..."}'
```

**Get all transactions:**
```bash
curl -X GET http://localhost:5000/api/transactions
```

**Get specific transaction:**
```bash
curl -X GET http://localhost:5000/api/transaction/abc123...
```

## 🗄️ Data Model

### 📋 Transaction
The Transaction model represents a Bitcoin transaction in the system with the following fields:

- 🔢 `id` (Integer): Primary key identifier
- 📄 `raw_tx` (Text): Raw transaction hex string
- 🆔 `txid` (String[64]): Unique transaction ID (SHA256 hash)
- 📊 `status` (String[20]): Transaction status (default: 'pending')
- 📅 `created_at` (DateTime): Creation timestamp
- 🔄 `updated_at` (DateTime): Last update timestamp
- 🔢 `push_attempts` (Integer): Number of push attempts (default: 0)
- 📝 `analysis_result` (Text): Result of transaction analysis

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
- **mempool.space**: Primary mempool service for transaction pushing and status checking
- **blockstream.info**: Alternative mempool service (configurable)

## 📝 License

This project is open source and available under the MIT License.
