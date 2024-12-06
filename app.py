from flask import Flask, render_template, request
from flask_login import LoginManager, current_user
from flask_jwt_extended import JWTManager, get_jwt_identity, verify_jwt_in_request
from config.settings import SECRET_KEY, JWT_SECRET_KEY, DEBUG
from config.logging_config import setup_logging
from controllers.auth_api import auth_api_bp
from controllers.consommation import consommation_bp
from controllers.items_api import items_api_bp
from models.user import User, users
from services.log_service import enregistrer_log
import logging

# Initialiser le logging
setup_logging()
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.secret_key = SECRET_KEY
    app.debug = DEBUG
    app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY

    # Setup JWT
    jwt = JWTManager(app)

    # Setup Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Désactiver le message "Please log in to access this page."
    login_manager.login_message = None
    login_manager.login_message_category = None

    @login_manager.user_loader
    def load_user(user_id):
        if user_id in users:
            return User(user_id)
        return None

    # Enregistrer les Blueprints
    from controllers.auth import auth_bp
    from controllers.api import api_bp
    from controllers.api_logs import api_logs_bp
    from controllers.dashboard import dashboard_bp

    app.register_blueprint(auth_bp, url_prefix='/')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(api_logs_bp, url_prefix='/api')
    app.register_blueprint(dashboard_bp, url_prefix='/')
    app.register_blueprint(auth_api_bp, url_prefix='/api')
    app.register_blueprint(items_api_bp, url_prefix='/api')
    app.register_blueprint(consommation_bp, url_prefix='/')

    # Liste des endpoints autorisés pour logs
    ALLOWED_ENDPOINTS = [
        "/api/test",
        "/api/another-test",
        "/api/items",  # Liste les items
        # On peut aussi rajouter la route dynamique en considérant un pattern
        # Mais comme c'est une route variable, difficile de lister toutes les versions de la route
        # "/api/items/<int:item_id>" ne pourra pas être compris tel quel
    ]

    @app.before_request
    def log_request_info():
        logger.info(f"Requête {request.method} {request.path} de {request.remote_addr}")

    @app.after_request
    def log_response_info(response):
        if request.path.startswith("/api/items"):
            user_id = None
            try:
                verify_jwt_in_request(optional=True)
                user_id = get_jwt_identity()
            except:
                pass

            # Déterminer si la réponse est binaire (image)
            content_type = response.headers.get("Content-Type", "")
            if "image" in content_type:
                # Ne pas appeler get_data() sur les images
                json_response = None
            else:
                json_response = response.get_data(as_text=True)

            if not user_id:
                user_id = "anonyme"

            try:
                method = request.method
                endpoint = request.path
                enregistrer_log(user_id, method, endpoint, json_response if json_response else "Binary response")
            except Exception as e:
                logger.error(f"Erreur dans log_response_info : {e}")
        return response

    @app.route('/')
    def home():
        logger.info("Accès à la page d'accueil")
        return render_template('home/index.html')



    return app
