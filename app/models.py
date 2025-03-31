from app import db
from datetime import datetime

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    raw_tx = db.Column(db.Text(), nullable=False)
    txid = db.Column(db.String(64), unique=True, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    push_attempts = db.Column(db.Integer, default=0)
    analysis_result = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'raw_tx': self.raw_tx,
            'txid': self.txid,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'push_attempts': self.push_attempts,
            'analysis_result': self.analysis_result
        } 