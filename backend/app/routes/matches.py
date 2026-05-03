from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.match import Match
from app.models.profile import Profile
from app.utils.helpers import compute_match_score

matches_bp = Blueprint('matches', __name__)


@matches_bp.route('/action', methods=['POST'])
@login_required
def like_or_pass():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    target_user_id = data.get('target_user_id')
    action = data.get('action')  # 'like' or 'pass'

    if not target_user_id or action not in ('like', 'pass'):
        return jsonify({'error': 'target_user_id and action (like/pass) required'}), 400

    if target_user_id == current_user.id:
        return jsonify({'error': 'Cannot like yourself'}), 400

    # Check not already acted
    existing = Match.query.filter_by(liker_id=current_user.id, liked_id=target_user_id).first()
    if existing:
        existing.action = action
        is_mutual = False
        if action == 'like':
            reverse = Match.query.filter_by(liker_id=target_user_id, liked_id=current_user.id, action='like').first()
            is_mutual = reverse is not None
            existing.is_mutual = is_mutual
            if reverse:
                reverse.is_mutual = True
        else:
            existing.is_mutual = False
        db.session.commit()
        return jsonify({'message': f'Action updated to {action}', 'is_mutual': is_mutual}), 200

    match = Match(liker_id=current_user.id, liked_id=target_user_id, action=action)

    is_mutual = False
    if action == 'like':
        reverse = Match.query.filter_by(liker_id=target_user_id, liked_id=current_user.id, action='like').first()
        if reverse:
            is_mutual = True
            match.is_mutual = True
            reverse.is_mutual = True

    db.session.add(match)
    db.session.commit()

    return jsonify({
        'message': f'Action recorded: {action}',
        'is_mutual': is_mutual,
        'match': match.to_dict()
    }), 201


@matches_bp.route('/mutual', methods=['GET'])
@login_required
def get_mutual_matches():
    """Return all users that mutually liked current user."""
    mutual = Match.query.filter_by(liker_id=current_user.id, action='like', is_mutual=True).all()
    result = []
    for m in mutual:
        profile = Profile.query.filter_by(user_id=m.liked_id).first()
        if profile:
            d = profile.to_dict()
            d['matched_at'] = m.created_at.isoformat()
            result.append(d)
    return jsonify({'matches': result, 'count': len(result)}), 200


@matches_bp.route('/count', methods=['GET'])
@login_required
def match_count():
    count = Match.query.filter_by(liker_id=current_user.id, action='like', is_mutual=True).count()
    return jsonify({'count': count}), 200


@matches_bp.route('/status/<int:target_user_id>', methods=['GET'])
@login_required
def match_status(target_user_id):
    my_action = Match.query.filter_by(liker_id=current_user.id, liked_id=target_user_id).first()
    their_action = Match.query.filter_by(liker_id=target_user_id, liked_id=current_user.id).first()
    return jsonify({
        'my_action': my_action.action if my_action else None,
        'their_action': their_action.action if their_action else None,
        'is_mutual': (my_action and their_action and
                      my_action.action == 'like' and their_action.action == 'like')
    }), 200
