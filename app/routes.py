from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for, abort
from app.models import Transaction
from app import db
from app.network_config import get_mempool_url, get_explorer_url, is_valid_network, VALID_NETWORKS
import requests
from bitcoinlib.transactions import Transaction as BtcTransaction

bp = Blueprint('main', __name__)

def get_service_url(network):
    """Get mempool service URL for a given network"""
    return get_mempool_url(network)

# Redirect root to mainchain
@bp.route('/')
def root():
    return redirect(url_for('main.index', network='mainchain'))

# Network-specific routes
@bp.route('/<network>/')
def index(network):
    if not is_valid_network(network):
        abort(404)
    return render_template('index.html', 
                         network=network, 
                         networks=VALID_NETWORKS,
                         onion_url=current_app.config['ONION_URL'])

@bp.route('/<network>/about')
def about(network):
    if not is_valid_network(network):
        abort(404)
    return render_template('about.html', 
                         network=network,
                         networks=VALID_NETWORKS,
                         onion_url=current_app.config['ONION_URL'])

@bp.route('/<network>/transactions')
def transactions(network):
    if not is_valid_network(network):
        abort(404)
    txs = Transaction.query.filter_by(network=network).order_by(Transaction.created_at.desc()).all()
    return render_template('transaction_list.html', 
                         transactions=txs, 
                         network=network,
                         networks=VALID_NETWORKS,
                         onion_url=current_app.config['ONION_URL'])

@bp.route('/<network>/transaction/<txid>')
def transaction_detail(network, txid):
    if not is_valid_network(network):
        abort(404)
    tx = Transaction.query.filter_by(txid=txid, network=network).first_or_404()
    explorer_url = get_explorer_url(network)
    mempool_url = get_mempool_url(network)
    return render_template('transaction_detail.html', 
                         tx=tx, 
                         network=network,
                         networks=VALID_NETWORKS,
                         explorer_url=explorer_url,
                         mempool_url=mempool_url,
                         onion_url=current_app.config['ONION_URL'])

@bp.route('/<network>/transaction/submit', methods=['POST'])
def submit_transaction(network):
    if not is_valid_network(network):
        abort(404)
    
    data = request.get_json()
    raw_tx = data.get('raw_tx')
    txid = data.get('txid')
    service = get_service_url(network)
    
    # Handle txid submission
    if txid:
        try:
            # Fetch transaction from service API
            response = requests.get(f'{service}/api/tx/{txid}/hex')
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

        # Check if transaction already exists for this network
        existing_tx = Transaction.query.filter_by(txid=calculated_txid, network=network).first()
        if existing_tx:
            return jsonify(existing_tx.to_dict()), 200

        # Create new transaction with calculated txid and network
        tx = Transaction(raw_tx=raw_tx, txid=calculated_txid, network=network)
        db.session.add(tx)
        db.session.commit()

        return jsonify(tx.to_dict()), 201
    
    except ValueError as e:
        return jsonify({'error': f'Invalid transaction format: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Error processing transaction: {str(e)}'}), 400

@bp.route('/<network>/transaction/<txid>/push', methods=['POST'])
def push_transaction(network, txid):
    if not is_valid_network(network):
        abort(404)
    
    tx = Transaction.query.filter_by(txid=txid, network=network).first_or_404()
    service = get_service_url(network)
    
    if tx.status == 'confirmed':
        return jsonify({
            'status': tx.status,
            'analysis_result': tx.analysis_result
        })

    try:
        # First check if transaction is already confirmed
        status_response = requests.get(f'{service}/api/tx/{txid}')
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
                f'{service}/api/tx',
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

@bp.route('/<network>/transaction/<txid>/delete', methods=['POST'])
def delete_transaction(network, txid):
    if not is_valid_network(network):
        abort(404)
    
    tx = Transaction.query.filter_by(txid=txid, network=network).first_or_404()
    
    # Only allow deletion of confirmed transactions
    if tx.status not in ['confirmed', 'failed']:
        return jsonify({
            'status': 'error',
            'error': 'Only confirmed or failed transactions can be deleted'
        }), 403
    
    db.session.delete(tx)
    db.session.commit()
    return jsonify({'status': 'success'})

# API Routes
@bp.route('/<network>/api/transactions', methods=['GET'])
def api_get_transactions(network):
    if not is_valid_network(network):
        abort(404)
    txs = Transaction.query.filter_by(network=network).order_by(Transaction.created_at.desc()).all()
    return jsonify([tx.to_dict() for tx in txs])

@bp.route('/<network>/api/transaction/<txid>', methods=['GET'])
def api_get_transaction(network, txid):
    if not is_valid_network(network):
        abort(404)
    tx = Transaction.query.filter_by(txid=txid, network=network).first()
    if not tx:
        return jsonify({'error': 'Transaction not found'}), 404
    return jsonify(tx.to_dict())

@bp.route('/<network>/api/transaction', methods=['POST'])
def api_post_txid(network):
    if not is_valid_network(network):
        abort(404)
    
    data = request.get_json()
    txid = data.get('txid')
    if not txid:
        return jsonify({'error': 'txid is required'}), 400
    
    service = get_service_url(network)
    
    try:
        response = requests.get(f'{service}/api/tx/{txid}/hex')
        if response.status_code != 200:
            return jsonify({'error': 'Transaction not found'}), 404
        raw_tx = response.text
        
        # Parse and validate
        tx = BtcTransaction.parse_hex(raw_tx)
        calculated_txid = tx.txid
        
        if txid != calculated_txid:
            return jsonify({'error': 'Invalid txid'}), 400
        
        # Check if transaction already exists for this network
        existing_tx = Transaction.query.filter_by(txid=calculated_txid, network=network).first()
        if existing_tx:
            return jsonify(existing_tx.to_dict()), 200
        
        # Save to database
        new_tx = Transaction(raw_tx=raw_tx, txid=calculated_txid, network=network)
        db.session.add(new_tx)
        db.session.commit()
        
        return jsonify(new_tx.to_dict()), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/<network>/api/transaction/push', methods=['POST'])
def api_push_tx(network):
    if not is_valid_network(network):
        abort(404)
    
    data = request.get_json()
    raw_tx = data.get('raw_tx')
    if not raw_tx:
        return jsonify({'error': 'raw_tx is required'}), 400
    
    service = get_service_url(network)
    
    try:
        # Validate hex format
        if not all(c in '0123456789abcdefABCDEF' for c in raw_tx):
            return jsonify({'error': 'Invalid hex format'}), 400
        
        # Parse transaction
        tx = BtcTransaction.parse_hex(raw_tx)
        txid = tx.txid
        
        # Check if transaction already exists for this network
        existing_tx = Transaction.query.filter_by(txid=txid, network=network).first()
        if existing_tx:
            # Update existing transaction
            new_tx = existing_tx
        else:
            # Save to database
            new_tx = Transaction(raw_tx=raw_tx, txid=txid, network=network)
            db.session.add(new_tx)
            db.session.commit()
        
        # Push to mempool
        response = requests.post(
            f'{service}/api/tx',
            data=raw_tx,
            headers={'Content-Type': 'text/plain'}
        )
        
        if response.status_code == 200:
            new_tx.status = 'success'
            new_tx.analysis_result = 'Transaction pushed successfully'
        else:
            new_tx.status = 'failed'
            new_tx.analysis_result = response.text
        
        new_tx.push_attempts += 1
        db.session.commit()
        
        return jsonify(new_tx.to_dict()), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400
