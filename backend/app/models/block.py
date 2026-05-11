"""
app/models/block.py
Place at: backend/app/models/block.py
"""
from app import db
from datetime import datetime


class Block(db.Model):
    __tablename__ = 'blocks'
    __table_args__ = (
        db.UniqueConstraint('blocker_id', 'blocked_id', name='unique_block'),
        db.Index('idx_block_blocker', 'blocker_id'),
        db.Index('idx_block_blocked', 'blocked_id'),
    )

    id         = db.Column(db.Integer, primary_key=True)
    blocker_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    blocked_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    blocker = db.relationship('User', foreign_keys=[blocker_id], backref='blocks_made')
    blocked = db.relationship('User', foreign_keys=[blocked_id], backref='blocked_by')

    def to_dict(self):
        return {
            'id':         self.id,
            'blocker_id': self.blocker_id,
            'blocked_id': self.blocked_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }