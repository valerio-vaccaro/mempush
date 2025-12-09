from app import db
from datetime import datetime
from app.network_config import VALID_NETWORKS, is_valid_network

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    raw_tx = db.Column(db.Text(), nullable=False)
    txid = db.Column(db.String(64), nullable=False)
    network = db.Column(db.String(20), nullable=False, default='mainchain')
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    push_attempts = db.Column(db.Integer, default=0)
    analysis_result = db.Column(db.Text)

    __table_args__ = (db.UniqueConstraint('txid', 'network', name='_txid_network_uc'),)

    def __init__(self, **kwargs):
        # Validate network if provided
        if 'network' in kwargs:
            network = kwargs['network']
            if not is_valid_network(network):
                raise ValueError(f"Invalid network: {network}. Valid networks are: {VALID_NETWORKS}")
        super(Transaction, self).__init__(**kwargs)

    def to_dict(self):
        return {
            'id': self.id,
            'raw_tx': self.raw_tx,
            'txid': self.txid,
            'network': self.network,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'push_attempts': self.push_attempts,
            'analysis_result': self.analysis_result
        } 

    @classmethod
    def get_by_network(cls, network):
        """Get all transactions for a specific network"""
        if not is_valid_network(network):
            raise ValueError(f"Invalid network: {network}. Valid networks are: {VALID_NETWORKS}")
        return cls.query.filter_by(network=network).order_by(cls.created_at.desc())

    @classmethod
    def get_by_txid_and_network(cls, txid, network):
        """Get a transaction by txid and network"""
        if not is_valid_network(network):
            raise ValueError(f"Invalid network: {network}. Valid networks are: {VALID_NETWORKS}")
        return cls.query.filter_by(txid=txid, network=network).first()

    @classmethod
    def exists_on_network(cls, txid, network):
        """Check if a transaction exists on a specific network"""
        if not is_valid_network(network):
            raise ValueError(f"Invalid network: {network}. Valid networks are: {VALID_NETWORKS}")
        return cls.query.filter_by(txid=txid, network=network).first() is not None

    def is_for_network(self, network):
        """Check if this transaction is for a specific network"""
        return self.network == network

    def __repr__(self):
        return f'<Transaction {self.txid[:16]}... on {self.network}>' 