from app import db
from datetime import datetime


class Report(db.Model):
    __tablename__ = 'reports'
    __table_args__ = (
        db.UniqueConstraint('reporter_id', 'reported_id', name='unique_report'),
        db.Index('idx_report_reported', 'reported_id'),
    )

    id          = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    reported_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    reason      = db.Column(db.String(50), nullable=False)   # spam | harassment | fake | inappropriate | other
    detail      = db.Column(db.Text)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    reporter = db.relationship('User', foreign_keys=[reporter_id], backref='reports_made')
    reported = db.relationship('User', foreign_keys=[reported_id], backref='reports_received')

    REASONS = ['spam', 'harassment', 'fake_profile', 'inappropriate_content', 'other']

    def to_dict(self):
        return {
            'id':          self.id,
            'reporter_id': self.reporter_id,
            'reported_id': self.reported_id,
            'reason':      self.reason,
            'detail':      self.detail,
            'created_at':  self.created_at.isoformat() if self.created_at else None,
        }