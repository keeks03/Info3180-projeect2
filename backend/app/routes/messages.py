from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.message import Message
from app.models.match import Match
from app.models.profile import Profile
from sqlalchemy import or_, and_

messages_bp = Blueprint('messages', __name__)


def are_mutual_matches(user_a_id, user_b_id):
    """Check if two users have mutually liked each other."""
    a_likes_b = Match.query.filter_by(liker_id=user_a_id, liked_id=user_b_id, action='like').first()
    b_likes_a = Match.query.filter_by(liker_id=user_b_id, liked_id=user_a_id, action='like').first()
    return bool(a_likes_b and b_likes_a)


@messages_bp.route('/send', methods=['POST'])
@login_required
def send_message():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    receiver_id = data.get('receiver_id')
    content = data.get('content', '').strip()

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

    messages = Message.query.filter(
        or_(
            and_(Message.sender_id == current_user.id, Message.receiver_id == other_user_id),
            and_(Message.sender_id == other_user_id, Message.receiver_id == current_user.id)
        )
    ).order_by(Message.created_at.asc()).all()

    # Mark received as read
    for m in messages:
        if m.receiver_id == current_user.id and not m.is_read:
            m.is_read = True
    db.session.commit()

    return jsonify({'messages': [m.to_dict() for m in messages]}), 200


@messages_bp.route('/conversations', methods=['GET'])
@login_required
def get_conversations():
    """Return list of conversations (one per match partner)."""
    mutual_matches = Match.query.filter_by(liker_id=current_user.id, action='like', is_mutual=True).all()

    conversations = []
    for match in mutual_matches:
        partner_id = match.liked_id
        profile = Profile.query.filter_by(user_id=partner_id).first()

        # Get last message
        last_msg = Message.query.filter(
            or_(
                and_(Message.sender_id == current_user.id, Message.receiver_id == partner_id),
                and_(Message.sender_id == partner_id, Message.receiver_id == current_user.id)
            )
        ).order_by(Message.created_at.desc()).first()

        # Unread count
        unread = Message.query.filter_by(
            sender_id=partner_id,
            receiver_id=current_user.id,
            is_read=False
        ).count()

        conversations.append({
            'partner_id': partner_id,
            'profile': profile.to_dict() if profile else None,
            'last_message': last_msg.to_dict() if last_msg else None,
            'unread_count': unread
        })

    # Sort by last message date
    conversations.sort(
        key=lambda x: x['last_message']['created_at'] if x['last_message'] else '',
        reverse=True
    )

    return jsonify({'conversations': conversations}), 200
