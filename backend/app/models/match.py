from app import db
from datetime import datetime


class Match(db.Model):
    """
    Stores like/pass actions between users.
    A mutual match exists when both users have liked each other.
    """
    __tablename__ = 'matches'
    __table_args__ = (
        db.UniqueConstraint('liker_id', 'liked_id', name='unique_like'),
        db.Index('idx_liker', 'liker_id'),
        db.Index('idx_liked', 'liked_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    liker_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    liked_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    action = db.Column(db.String(10), nullable=False)  # 'like' or 'pass'
    is_mutual = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'liker_id': self.liker_id,
            'liked_id': self.liked_id,
            'action': self.action,
            'is_mutual': self.is_mutual,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
