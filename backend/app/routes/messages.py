from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.message import Message
from app.models.match import Match
from app.models.profile import Profile
from sqlalchemy import or_, and_

messages_bp = Blueprint('messages', __name__)

SIG_PREFIX = '__WEBRTC__'


def are_mutual_matches(user_a_id, user_b_id):
    a_likes_b = Match.query.filter_by(liker_id=user_a_id, liked_id=user_b_id, action='like').first()
    b_likes_a = Match.query.filter_by(liker_id=user_b_id, liked_id=user_a_id, action='like').first()
    return bool(a_likes_b and b_likes_a)


def send_system_message(sender_id, receiver_id, content):
    """Write a notice into both sides of the conversation."""
    for s, r in [(sender_id, receiver_id), (receiver_id, sender_id)]:
        db.session.add(Message(sender_id=s, receiver_id=r, content=content))
    db.session.commit()


@messages_bp.route('/send', methods=['POST'])
@login_required
def send_message():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    receiver_id = data.get('receiver_id')
    content     = (data.get('content') or '').strip()

    if not receiver_id or not content:
        return jsonify({'error': 'receiver_id and content are required'}), 400

    if receiver_id == current_user.id:
        return jsonify({'error': 'Cannot message yourself'}), 400

    if not are_mutual_matches(current_user.id, receiver_id):
        return jsonify({'error': 'You can only message mutual matches'}), 403

    msg = Message(sender_id=current_user.id, receiver_id=receiver_id, content=content)
    db.session.add(msg)
    db.session.commit()
    return jsonify({'message': 'Message sent', 'data': msg.to_dict()}), 201


@messages_bp.route('/conversation/<int:other_user_id>', methods=['GET'])
@login_required
def get_conversation(other_user_id):
    if not are_mutual_matches(current_user.id, other_user_id):
        return jsonify({'error': 'No match found'}), 403

    msgs = Message.query.filter(
        or_(
            and_(Message.sender_id == current_user.id, Message.receiver_id == other_user_id),
            and_(Message.sender_id == other_user_id, Message.receiver_id == current_user.id)
        )
    ).order_by(Message.created_at.asc()).all()

    for m in msgs:
        if m.receiver_id == current_user.id and not m.is_read:
            m.is_read = True
    db.session.commit()

    return jsonify({'messages': [m.to_dict() for m in msgs]}), 200


@messages_bp.route('/conversation/<int:other_user_id>/call-started', methods=['POST'])
@login_required
def call_started(other_user_id):
    """
    Called by VideoCallView the moment both peers connect.
    The frontend sends the pre-formatted LOCAL time string so the backend
    never needs to know the user's timezone.
    """
    if not are_mutual_matches(current_user.id, other_user_id):
        return jsonify({'error': 'No match found'}), 403

    data             = request.get_json(silent=True) or {}
    started_at_local = data.get('started_at_local', 'unknown time')

    notice = f'📹 Video call started\n🕐 {started_at_local}'
    send_system_message(current_user.id, other_user_id, notice)

    return jsonify({'message': 'Call started notice sent'}), 200


@messages_bp.route('/conversation/<int:other_user_id>/cleanup-signals', methods=['DELETE'])
@login_required
def cleanup_signals(other_user_id):
    """
    Called by VideoCallView when a call ends.
    Frontend sends both started_at_local and ended_at_local as pre-formatted
    strings in the user's own timezone — the server just stores them as-is.
    """
    if not are_mutual_matches(current_user.id, other_user_id):
        return jsonify({'error': 'No match found'}), 403

    data             = request.get_json(silent=True) or {}
    started_at_local = data.get('started_at_local')
    ended_at_local   = data.get('ended_at_local', 'unknown time')

    if started_at_local:
        notice = (
            f'Video call ended\n'
            f'▶ Started:  {started_at_local}\n'
            f'⏹ Ended:    {ended_at_local}'
        )
    else:
        notice = f' Video call ended\n⏹ {ended_at_local}'

    send_system_message(current_user.id, other_user_id, notice)

    # Delete all raw WebRTC signal messages
    deleted = Message.query.filter(
        or_(
            and_(Message.sender_id == current_user.id, Message.receiver_id == other_user_id),
            and_(Message.sender_id == other_user_id, Message.receiver_id == current_user.id)
        ),
        Message.content.like(f'{SIG_PREFIX}%')
    ).delete(synchronize_session=False)

    db.session.commit()
    return jsonify({'message': f'Cleaned up {deleted} signal messages'}), 200


@messages_bp.route('/conversations', methods=['GET'])
@login_required
def get_conversations():
    mutual_matches = Match.query.filter_by(
        liker_id=current_user.id, action='like', is_mutual=True
    ).all()

    conversations = []
    for match in mutual_matches:
        partner_id = match.liked_id
        profile    = Profile.query.filter_by(user_id=partner_id).first()

        last_msg = Message.query.filter(
            or_(
                and_(Message.sender_id == current_user.id, Message.receiver_id == partner_id),
                and_(Message.sender_id == partner_id, Message.receiver_id == current_user.id)
            ),
            ~Message.content.like(f'{SIG_PREFIX}%')
        ).order_by(Message.created_at.desc()).first()

        unread = Message.query.filter(
            Message.sender_id == partner_id,
            Message.receiver_id == current_user.id,
            Message.is_read == False,
            ~Message.content.like(f'{SIG_PREFIX}%')
        ).count()

        conversations.append({
            'partner_id':   partner_id,
            'profile':      profile.to_dict() if profile else None,
            'last_message': last_msg.to_dict() if last_msg else None,
            'unread_count': unread,
        })

    conversations.sort(
        key=lambda x: x['last_message']['created_at'] if x['last_message'] else '',
        reverse=True
    )

    return jsonify({'conversations': conversations}), 200