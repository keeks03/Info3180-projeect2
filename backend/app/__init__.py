from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_login import LoginManager
from app.routes import main_bp
import os

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()


def create_app(config_class=None):
    app = Flask(__name__)

    if config_class is None:
        from config import Config
        app.config.from_object(Config)
    else:
        app.config.from_object(config_class)


     # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Configure CORS
    CORS(
        app, 
         supports_credentials=True, 
         origins=app.config.get('CORS_ORIGINS'),
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
         allow_headers=['Content-Type', 'Authorization']
    )

    # Ensures that upload folder exists
    upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)

   

    
    
    # Import models so Flask-Migrate picks them up
    from app.models import user, profile, match, message, favourite

    with app.app_context():
        db.create_all()
        print("✅ Database tables created/verified!")


    # Register blueprint
    from app.routes.auth import auth_bp
    from app.routes.profiles import profiles_bp
    from app.routes.matches import matches_bp
    from app.routes.messages import messages_bp
    from app.routes.search import search_bp
    from app.routes.favourites import favourites_bp


    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(profiles_bp, url_prefix='/api/profiles')
    app.register_blueprint(matches_bp, url_prefix='/api/matches')
    app.register_blueprint(messages_bp, url_prefix='/api/messages')
    app.register_blueprint(search_bp, url_prefix='/api/search')
    app.register_blueprint(favourites_bp, url_prefix='/api/favourites')

    

    return app
