from app import db
from datetime import datetime


class Favourite(db.Model):
    __tablename__ = 'favourites'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'profile_id', name='unique_favourite'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    profile = db.relationship('Profile', backref='favourited_by', lazy='joined')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'profile_id': self.profile_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
