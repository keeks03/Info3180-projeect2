"""
app/routes/moderation.py
Place at: backend/app/routes/moderation.py

Register in backend/app/__init__.py:
    from app.routes.moderation import moderation_bp
    app.register_blueprint(moderation_bp, url_prefix='/api/moderation')

Also import models in __init__.py create_app():
    from app.models import user, profile, match, message, favourite, report, block
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models.report import Report
from app.models.block import Block
from app.models.user import User
from app.models.match import Match

moderation_bp = Blueprint('moderation', __name__)


# ── REPORT ────────────────────────────────────────────────────────────────────

@moderation_bp.route('/report', methods=['POST'])
@login_required
def report_user():
    data        = request.get_json(force=True, silent=True) or {}
    reported_id = data.get('reported_id')
    reason      = (data.get('reason') or '').strip()
    detail      = (data.get('detail') or '').strip()[:500]

    if not reported_id:
        return jsonify({'error': 'reported_id is required'}), 400

    if reason not in Report.REASONS:
        return jsonify({'error': f'reason must be one of: {Report.REASONS}'}), 400

    if reported_id == current_user.id:
        return jsonify({'error': 'You cannot report yourself'}), 400

    target = User.query.get(reported_id)
    if not target:
        return jsonify({'error': 'User not found'}), 404

    # Upsert — update reason if already reported
    existing = Report.query.filter_by(
        reporter_id=current_user.id, reported_id=reported_id
    ).first()

    if existing:
        existing.reason = reason
        existing.detail = detail
    else:
        db.session.add(Report(
            reporter_id=current_user.id,
            reported_id=reported_id,
            reason=reason,
            detail=detail,
        ))

    db.session.commit()
    return jsonify({'message': 'Report submitted. Thank you for keeping DriftDater safe.'}), 200


# ── BLOCK ─────────────────────────────────────────────────────────────────────

@moderation_bp.route('/block', methods=['POST'])
@login_required
def block_user():
    data       = request.get_json(force=True, silent=True) or {}
    blocked_id = data.get('blocked_id')

    if not blocked_id:
        return jsonify({'error': 'blocked_id is required'}), 400

    if blocked_id == current_user.id:
        return jsonify({'error': 'You cannot block yourself'}), 400

    target = User.query.get(blocked_id)
    if not target:
        return jsonify({'error': 'User not found'}), 404

    existing = Block.query.filter_by(
        blocker_id=current_user.id, blocked_id=blocked_id
    ).first()

    if existing:
        return jsonify({'message': 'Already blocked', 'blocked': True}), 200

    db.session.add(Block(blocker_id=current_user.id, blocked_id=blocked_id))

    # Also remove any mutual match between the two users
    Match.query.filter(
        ((Match.liker_id == current_user.id) & (Match.liked_id == blocked_id)) |
        ((Match.liker_id == blocked_id)      & (Match.liked_id == current_user.id))
    ).delete(synchronize_session=False)

    db.session.commit()
    return jsonify({'message': f'{target.username} has been blocked.', 'blocked': True}), 200


@moderation_bp.route('/block/<int:blocked_id>', methods=['DELETE'])
@login_required
def unblock_user(blocked_id):
    block = Block.query.filter_by(
        blocker_id=current_user.id, blocked_id=blocked_id
    ).first()

    if not block:
        return jsonify({'error': 'Block not found'}), 404

    db.session.delete(block)
    db.session.commit()
    return jsonify({'message': 'User unblocked.', 'blocked': False}), 200


@moderation_bp.route('/block/check/<int:user_id>', methods=['GET'])
@login_required
def check_block(user_id):
    i_blocked_them  = Block.query.filter_by(blocker_id=current_user.id, blocked_id=user_id).first()
    they_blocked_me = Block.query.filter_by(blocker_id=user_id, blocked_id=current_user.id).first()
    return jsonify({
        'i_blocked_them':  bool(i_blocked_them),
        'they_blocked_me': bool(they_blocked_me),
        'any_block':       bool(i_blocked_them or they_blocked_me),
    }), 200


@moderation_bp.route('/blocks', methods=['GET'])
@login_required
def get_my_blocks():
    blocks = Block.query.filter_by(blocker_id=current_user.id).all()
    result = []
    for b in blocks:
        u = User.query.get(b.blocked_id)
        if u:
            result.append({
                'blocked_id':  b.blocked_id,
                'username':    u.username,
                'name':        f'{u.profile.first_name} {u.profile.last_name}' if u.profile else u.username,
                'picture':     u.profile.profile_picture if u.profile else None,
                'blocked_at':  b.created_at.isoformat() if b.created_at else None,
            })
    return jsonify({'blocks': result}), 200