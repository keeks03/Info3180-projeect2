import os
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from flask_login import login_required, current_user
from app import db
from app.models.profile import Profile, Interest
from app.models.block import Block
from app.utils.helpers import save_profile_picture, compute_match_score
from datetime import datetime

profiles_bp = Blueprint('profiles', __name__)


def get_or_create_interest(name):
    name = name.strip().lower()
    interest = Interest.query.filter_by(name=name).first()
    if not interest:
        interest = Interest(name=name)
        db.session.add(interest)
    return interest


def get_blocked_ids():
    """Return set of user_ids that should be hidden from the current user —
    anyone they blocked OR anyone who blocked them."""
    i_blocked = {b.blocked_id for b in Block.query.filter_by(blocker_id=current_user.id).all()}
    blocked_me = {b.blocker_id for b in Block.query.filter_by(blocked_id=current_user.id).all()}
    return i_blocked | blocked_me


@profiles_bp.route('', methods=['POST'])
@login_required
def create_profile():
    if current_user.profile:
        return jsonify({'error': 'Profile already exists'}), 409

    data = request.form.to_dict()
    file = request.files.get('profile_picture')

    if not data.get('first_name', '').strip():
        return jsonify({'error': 'First name is required'}), 400
    if not data.get('last_name', '').strip():
        return jsonify({'error': 'Last name is required'}), 400
    if not data.get('date_of_birth', '').strip():
        return jsonify({'error': 'Date of birth is required'}), 400
    if not data.get('gender', '').strip():
        return jsonify({'error': 'Gender is required'}), 400

    try:
        dob = datetime.strptime(data['date_of_birth'].strip(), '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    profile = Profile(
        user_id=current_user.id,
        first_name=data['first_name'].strip(),
        last_name=data['last_name'].strip(),
        date_of_birth=dob,
        gender=data.get('gender', 'other').strip(),
        looking_for=data.get('looking_for', 'any'),
        bio=data.get('bio', ''),
        city=data.get('city', ''),
        country=data.get('country', ''),
        occupation=data.get('occupation', ''),
        education_level=data.get('education_level', ''),
        is_public=data.get('is_public', 'true').lower() == 'true',
        min_age_preference=int(data.get('min_age_preference', 18) or 18),
        max_age_preference=int(data.get('max_age_preference', 99) or 99),
        max_distance_km=int(data.get('max_distance_km', 100) or 100),
    )

    if data.get('latitude'):
        profile.latitude = float(data['latitude'])
    if data.get('longitude'):
        profile.longitude = float(data['longitude'])

    interest_names = request.form.getlist('interests')
    if isinstance(interest_names, str):
        interest_names = [interest_names]
    for name in interest_names:
        if name:
            profile.interests.append(get_or_create_interest(name))

    if file and file.filename:
        filename = save_profile_picture(file)
        if filename:
            profile.profile_picture = filename

    db.session.add(profile)
    db.session.commit()
    return jsonify({'message': 'Profile created', 'profile': profile.to_dict(include_private=True)}), 201


@profiles_bp.route('/me', methods=['GET'])
@login_required
def get_my_profile():
    profile = current_user.profile
    if not profile:
        return jsonify({'error': 'No profile found'}), 404
    return jsonify({'profile': profile.to_dict(include_private=True)}), 200


@profiles_bp.route('/me', methods=['PUT'])
@login_required
def update_my_profile():
    profile = current_user.profile
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404

    data = request.form.to_dict()
    file = request.files.get('profile_picture')

    if data.get('first_name'):       profile.first_name = data['first_name'].strip()
    if data.get('last_name'):        profile.last_name  = data['last_name'].strip()
    if data.get('date_of_birth'):
        try:
            profile.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
    if data.get('gender'):           profile.gender          = data['gender']
    if data.get('looking_for'):      profile.looking_for     = data['looking_for']
    if data.get('bio') is not None:  profile.bio             = data['bio']
    if data.get('city') is not None: profile.city            = data['city']
    if data.get('country') is not None: profile.country      = data['country']
    if data.get('occupation') is not None: profile.occupation = data['occupation']
    if data.get('education_level') is not None: profile.education_level = data['education_level']
    if data.get('is_public') is not None: profile.is_public  = data['is_public'].lower() == 'true'
    if data.get('min_age_preference'): profile.min_age_preference = int(data['min_age_preference'])
    if data.get('max_age_preference'): profile.max_age_preference = int(data['max_age_preference'])
    if data.get('max_distance_km'):    profile.max_distance_km    = int(data['max_distance_km'])
    if data.get('latitude'):           profile.latitude  = float(data['latitude'])
    if data.get('longitude'):          profile.longitude = float(data['longitude'])

    interest_names = request.form.getlist('interests')
    if interest_names:
        profile.interests.clear()
        for name in interest_names:
            if name:
                profile.interests.append(get_or_create_interest(name))

    if file and file.filename:
        if profile.profile_picture:
            old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], profile.profile_picture)
            if os.path.exists(old_path):
                os.remove(old_path)
        filename = save_profile_picture(file)
        if filename:
            profile.profile_picture = filename

    db.session.commit()
    return jsonify({'message': 'Profile updated', 'profile': profile.to_dict(include_private=True)}), 200


@profiles_bp.route('/<int:user_id>', methods=['GET'])
@login_required
def get_profile(user_id):
    # Block check — neither side can view the other's profile
    blocked_ids = get_blocked_ids()
    if user_id in blocked_ids:
        return jsonify({'error': 'Profile not found'}), 404

    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404
    if not profile.is_public and profile.user_id != current_user.id:
        return jsonify({'error': 'Profile is private'}), 403

    data = profile.to_dict()
    if current_user.profile and profile.user_id != current_user.id:
        data['match_score'] = compute_match_score(current_user.profile, profile)
    return jsonify({'profile': data}), 200


@profiles_bp.route('/picture/<filename>', methods=['GET'])
def get_picture(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


@profiles_bp.route('/browse', methods=['GET'])
@login_required
def browse_profiles():
    my_profile = current_user.profile
    if not my_profile:
        return jsonify({'error': 'Create your profile first'}), 400

    # IDs to exclude: already acted on + self + any block (either direction)
    excluded_ids = {m.liked_id for m in current_user.likes_given}
    excluded_ids.add(current_user.id)
    excluded_ids |= get_blocked_ids()

    profiles = Profile.query.filter(
        Profile.user_id.notin_(excluded_ids),
        Profile.is_public == True
    ).all()

    result = []
    for p in profiles:
        d = p.to_dict()
        d['match_score'] = compute_match_score(my_profile, p)
        result.append(d)

    result.sort(key=lambda x: x['match_score'], reverse=True)
    return jsonify({'profiles': result}), 200