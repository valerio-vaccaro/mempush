from flask import Blueprint, render_template, request, jsonify
from app.models import Transaction
from app import db
import requests
from bitcoinlib.transactions import Transaction as BtcTransaction

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/transactions')
def transactions():
    txs = Transaction.query.order_by(Transaction.created_at.desc()).all()
    return render_template('transaction_list.html', transactions=txs)

@bp.route('/transaction/<txid>')
def transaction_detail(txid):
    tx = Transaction.query.filter_by(txid=txid).first_or_404()
    return render_template('transaction_detail.html', tx=tx)

@bp.route('/transaction/submit', methods=['POST'])
def submit_transaction():
    data = request.get_json()
    raw_tx = data.get('raw_tx')
    txid = data.get('txid')
    
    # Handle txid submission
    if txid:
        try:
            # Fetch transaction from Blockstream API
            response = requests.get(f'https://blockstream.info/api/tx/{txid}/hex')
            if response.status_code != 200:
                return jsonify({'error': 'Transaction not found'}), 404
            raw_tx = response.text
        except Exception as e:
            return jsonify({'error': f'Error fetching transaction: {str(e)}'}), 400
    
    # Basic validation
    if not raw_tx:
        return jsonify({'error': 'Raw transaction is required'}), 400

    # Validate hex format
    try:
        # Check if string contains only valid hex characters
        if not all(c in '0123456789abcdefABCDEF' for c in raw_tx):
            return jsonify({'error': 'Raw transaction must contain only hexadecimal characters'}), 400
        
        # Parse transaction using bitcoinlib
        tx = BtcTransaction.parse_hex(raw_tx)
        # Get txid using the library's built-in function
        calculated_txid = tx.txid
        
        # If txid was provided, verify it matches
        if txid and txid != calculated_txid:
            return jsonify({'error': 'Provided txid does not match calculated txid'}), 400

        # Create new transaction with calculated txid
        tx = Transaction(raw_tx=raw_tx, txid=calculated_txid)
        db.session.add(tx)
        db.session.commit()

        return jsonify(tx.to_dict()), 201
    
    except ValueError as e:
        return jsonify({'error': f'Invalid transaction format: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Error processing transaction: {str(e)}'}), 400

@bp.route('/transaction/<txid>/push', methods=['POST'])
def push_transaction(txid):
    tx = Transaction.query.filter_by(txid=txid).first_or_404()
    
    if tx.status == 'confirmed':
        return jsonify({
            'status': tx.status,
            'analysis_result': tx.analysis_result
        })

    try:
        # First check if transaction is already confirmed
        status_response = requests.get(f'https://blockstream.info/api/tx/{txid}')
        if status_response.status_code == 200:
            status_data = status_response.json()
            if status_data.get('status', {}).get('confirmed'):
                tx.status = 'confirmed'
                tx.analysis_result = 'Transaction is already confirmed in the blockchain'
                db.session.commit()
                return jsonify({
                    'status': tx.status,
                    'analysis_result': tx.analysis_result
                })
            else:
                tx.status = 'success'
                tx.analysis_result = 'Transaction is already present in mempool'
                db.session.commit()
                return jsonify({
                    'status': tx.status,
                    'analysis_result': tx.analysis_result
                })
        elif status_response.status_code == 404:

            # If not confirmed, proceed with pushing
            response = requests.post(
                'https://blockstream.info/api/tx',
                data=tx.raw_tx,
                headers={'Content-Type': 'text/plain'}
            )

            # Store the API response
            tx.analysis_result = response.text
        
            if response.status_code == 200:
                tx.status = 'success'
            else:
                tx.status = 'failed'
        
            tx.push_attempts += 1
            db.session.commit()
        
            return jsonify({
                'status': tx.status,
                'push_attempts': tx.push_attempts,
                'analysis_result': tx.analysis_result
            })
        
    except Exception as e:
        tx.status = 'error'
        tx.analysis_result = str(e)
        tx.push_attempts += 1
        db.session.commit()
        return jsonify({
            'status': 'error',
            'error': str(e),
            'analysis_result': tx.analysis_result
        }), 500

@bp.route('/transaction/<txid>/delete', methods=['POST'])
def delete_transaction(txid):
    tx = Transaction.query.filter_by(txid=txid).first_or_404()
    
    # Only allow deletion of confirmed transactions
    if tx.status != 'confirmed':
        return jsonify({
            'status': 'error',
            'error': 'Only confirmed transactions can be deleted'
        }), 403
    
    db.session.delete(tx)
    db.session.commit()
    return jsonify({'status': 'success'}) 