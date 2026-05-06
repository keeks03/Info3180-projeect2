@main_bp.route('/')
def index():
    return {'message': 'DriftDater API is running!'}

@main_bp.route('/api/health')
def health():
    return {'status': 'ok', 'message': 'API is working'}