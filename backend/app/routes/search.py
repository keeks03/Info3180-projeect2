from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models.profile import Profile, Interest
from app.models.block import Block
from app.utils.helpers import compute_match_score
from app import db

search_bp = Blueprint('search', __name__)


def get_blocked_ids():
    """Return set of user_ids hidden due to any block (either direction)."""
    i_blocked  = {b.blocked_id  for b in Block.query.filter_by(blocker_id=current_user.id).all()}
    blocked_me = {b.blocker_id  for b in Block.query.filter_by(blocked_id=current_user.id).all()}
    return i_blocked | blocked_me


@search_bp.route('', methods=['GET'])
@login_required
def search_profiles():
    my_profile = current_user.profile

    name_query = request.args.get('name', '').strip()
    city       = request.args.get('city', '').strip()
    country    = request.args.get('country', '').strip()
    min_age    = request.args.get('min_age', type=int)
    max_age    = request.args.get('max_age', type=int)
    gender     = request.args.get('gender', '').strip()
    interests  = request.args.getlist('interests')
    sort_by    = request.args.get('sort', 'match_score')

    blocked_ids = get_blocked_ids()
    excluded    = blocked_ids | {current_user.id}

    query = Profile.query.filter(
        Profile.user_id.notin_(excluded),
        Profile.is_public == True
    )

    if name_query:
        like = f'%{name_query}%'
        query = query.filter(
            db.or_(
                Profile.first_name.ilike(like),
                Profile.last_name.ilike(like),
                Profile.bio.ilike(like)
            )
        )

    if city:    query = query.filter(Profile.city.ilike(f'%{city}%'))
    if country: query = query.filter(Profile.country.ilike(f'%{country}%'))
    if gender:  query = query.filter(Profile.gender == gender)

    profiles = query.all()

    # Age filter (computed from DOB, not stored)
    if min_age is not None or max_age is not None:
        filtered = []
        for p in profiles:
            age = p.age()
            if min_age and age < min_age: continue
            if max_age and age > max_age: continue
            filtered.append(p)
        profiles = filtered

    # Interest filter
    if interests:
        filtered = []
        for p in profiles:
            p_interests = {i.name for i in p.interests}
            if any(i.lower() in p_interests for i in interests):
                filtered.append(p)
        profiles = filtered

    result = []
    for p in profiles:
        d = p.to_dict()
        d['match_score'] = compute_match_score(my_profile, p) if my_profile else 0
        result.append(d)

    if sort_by == 'newest':
        result.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    elif sort_by == 'name':
        result.sort(key=lambda x: x.get('first_name', ''))
    else:
        result.sort(key=lambda x: x.get('match_score', 0), reverse=True)

    return jsonify({'profiles': result, 'count': len(result)}), 200


@search_bp.route('/interests', methods=['GET'])
@login_required
def get_all_interests():
    interests = Interest.query.order_by(Interest.name).all()
    return jsonify({'interests': [i.to_dict() for i in interests]}), 200