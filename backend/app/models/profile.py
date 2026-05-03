from app import db
from datetime import datetime


# Many-to-many: profiles <-> interests
profile_interests = db.Table(
    'profile_interests',
    db.Column('profile_id', db.Integer, db.ForeignKey('profiles.id', ondelete='CASCADE'), primary_key=True),
    db.Column('interest_id', db.Integer, db.ForeignKey('interests.id', ondelete='CASCADE'), primary_key=True)
)


class Interest(db.Model):
    __tablename__ = 'interests'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)

    def to_dict(self):
        return {'id': self.id, 'name': self.name}


class Profile(db.Model):
    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False, index=True)

    # Basic info
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(20), nullable=False)  # male, female, non-binary, other
    looking_for = db.Column(db.String(20), default='any')  # male, female, any

    # Bio & description
    bio = db.Column(db.Text)

    # Location
    city = db.Column(db.String(100), index=True)
    country = db.Column(db.String(100), index=True)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    # Preferences
    min_age_preference = db.Column(db.Integer, default=18)
    max_age_preference = db.Column(db.Integer, default=99)
    max_distance_km = db.Column(db.Integer, default=100)

    # Profile picture
    profile_picture = db.Column(db.String(255))

    # Custom fields (additional required fields)
    occupation = db.Column(db.String(100))
    education_level = db.Column(db.String(50))  # high_school, bachelor, master, phd, other

    # Visibility
    is_public = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    interests = db.relationship('Interest', secondary=profile_interests, backref='profiles', lazy='subquery')

    def age(self):
        from datetime import date
        today = date.today()
        dob = self.date_of_birth
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    def to_dict(self, include_private=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'age': self.age(),
            'gender': self.gender,
            'looking_for': self.looking_for,
            'bio': self.bio,
            'city': self.city,
            'country': self.country,
            'occupation': self.occupation,
            'education_level': self.education_level,
            'interests': [i.to_dict() for i in self.interests],
            'profile_picture': self.profile_picture,
            'is_public': self.is_public,
            'min_age_preference': self.min_age_preference,
            'max_age_preference': self.max_age_preference,
            'max_distance_km': self.max_distance_km,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_private:
            data['date_of_birth'] = self.date_of_birth.isoformat() if self.date_of_birth else None
            data['latitude'] = self.latitude
            data['longitude'] = self.longitude
        return data
