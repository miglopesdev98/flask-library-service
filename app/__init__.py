from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager, get_jwt_identity, verify_jwt_in_request
from config import config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

# Create the application factory
def create_app(config_name='default'):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize JWT
    jwt.init_app(app)
    
    # Configure CORS
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": app.config.get('CORS_ORIGINS', []),
                "supports_credentials": True,
                "allow_headers": ["Content-Type", "Authorization", "X-CSRF-TOKEN"],
                "expose_headers": ["X-CSRF-TOKEN"],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
            }
        },
        supports_credentials=True
    )
    
    # JWT configuration
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return user['id']
    
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        from app.models import User
        identity = jwt_data["sub"]
        return User.query.get(identity)
    
    # JWT error handlers
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'message': 'Missing authorization token',
            'error': 'authorization_required'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'message': 'Invalid or expired token',
            'error': 'invalid_token'
        }), 401
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'message': 'Token has expired',
            'error': 'token_expired'
        }), 401
    
    # Register blueprints
    from app.books import routes as books_routes
    from app.library import routes as library_routes
    from app.auth import auth_bp
    
    # Register blueprints with URL prefixes
    app.register_blueprint(books_routes.bp, url_prefix='/api/books')
    app.register_blueprint(library_routes.bp, url_prefix='/api/library')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Add CORS headers to all responses
    @app.after_request
    def after_request(response):
        # Add CORS headers
        response.headers.add('Access-Control-Allow-Origin', 
                           request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers',
                           'Content-Type,Authorization,X-CSRF-TOKEN')
        response.headers.add('Access-Control-Allow-Methods',
                           'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    return app
