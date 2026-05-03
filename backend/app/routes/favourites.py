from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.favourite import Favourite
from app.models.profile import Profile
from app.utils.helpers import compute_match_score

favourites_bp = Blueprint('favourites', __name__)


@favourites_bp.route('', methods=['GET'])
@login_required
def get_favourites():
    favs = Favourite.query.filter_by(user_id=current_user.id).all()
    result = []
    for f in favs:
        profile = f.profile
        if profile:
            d = profile.to_dict()
            d['favourited_at'] = f.created_at.isoformat()
            if current_user.profile:
                d['match_score'] = compute_match_score(current_user.profile, profile)
            result.append(d)
    return jsonify({'favourites': result}), 200


@favourites_bp.route('', methods=['POST'])
@login_required
def add_favourite():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    profile_id = data.get('profile_id')
    if not profile_id:
        return jsonify({'error': 'profile_id is required'}), 400

    profile = Profile.query.get(profile_id)
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404

    if profile.user_id == current_user.id:
        return jsonify({'error': 'Cannot favourite yourself'}), 400

    existing = Favourite.query.filter_by(user_id=current_user.id, profile_id=profile_id).first()
    if existing:
        return jsonify({'error': 'Already in favourites'}), 409

    fav = Favourite(user_id=current_user.id, profile_id=profile_id)
    db.session.add(fav)
    db.session.commit()
    return jsonify({'message': 'Added to favourites', 'favourite': fav.to_dict()}), 201


@favourites_bp.route('/<int:profile_id>', methods=['DELETE'])
@login_required
def remove_favourite(profile_id):
    fav = Favourite.query.filter_by(user_id=current_user.id, profile_id=profile_id).first()
    if not fav:
        return jsonify({'error': 'Not in favourites'}), 404
    db.session.delete(fav)
    db.session.commit()
    return jsonify({'message': 'Removed from favourites'}), 200


@favourites_bp.route('/check/<int:profile_id>', methods=['GET'])
@login_required
def check_favourite(profile_id):
    fav = Favourite.query.filter_by(user_id=current_user.id, profile_id=profile_id).first()
    return jsonify({'is_favourite': fav is not None}), 200
