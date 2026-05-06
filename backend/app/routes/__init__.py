from flask import Blueprint


main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return {'message': 'DriftDater API is live!'}

@main_bp.route('/api/health')
def health():
    return {'status': 'ok', 'message': 'API is working'}