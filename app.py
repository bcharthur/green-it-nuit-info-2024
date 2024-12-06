from flask import Flask, render_template, request
from flask_login import LoginManager, current_user
from flask_jwt_extended import JWTManager, get_jwt_identity, verify_jwt_in_request

from config.connection_db import get_db_connection
from config.settings import SECRET_KEY, JWT_SECRET_KEY, DEBUG
from config.logging_config import setup_logging
from controllers.auth_api import auth_api_bp
from controllers.consommation import consommation_bp
from controllers.items_api import items_api_bp
from models.user import User, users
from services.log_service import enregistrer_log
from config.setup_db import main as setup_database

import logging

# Initialiser le logging
setup_logging()
logger = logging.getLogger(__name__)

# Avant de créer l'app, vous pouvez appeler:
setup_database()

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
        # Vérifier si le chemin commence par "/api" mais n'est pas exactement "/api"
        if request.path.startswith("/api") and request.path != "/api":
            # Vérifier si le chemin est dans ALLOWED_ENDPOINTS ou correspond à un pattern
            if request.path in ALLOWED_ENDPOINTS or re.match(r'^/api/items/\d+$', request.path):
                # Votre logique de log ici, par exemple :
                user_id = None
                try:
                    verify_jwt_in_request(optional=True)
                    user_id = get_jwt_identity()
                except:
                    pass

                # Déterminer si la réponse est binaire (image)
                content_type = response.headers.get("Content-Type", "")
                if "image" in content_type:
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

        # Initialiser les variables
        total_co2 = 0
        image_count = 0

        # Obtenir la connexion à la base de données
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                # Récupérer le total de CO2 économisé
                cursor.execute("SELECT SUM(co2_economise) FROM image_stats")
                result = cursor.fetchone()
                total_co2 = result[0] if result[0] is not None else 0

                # Récupérer le nombre total d'images traitées
                cursor.execute("SELECT COUNT(*) FROM image_stats")
                result = cursor.fetchone()
                image_count = result[0] if result[0] is not None else 0

                # Convertir le CO2 en kilogrammes pour une meilleure lisibilité
                total_co2_kg = total_co2 / 1000  # Supposant que co2_economise est en grammes

            except Exception as e:
                logger.error(f"Erreur lors de la récupération des statistiques : {e}")
            finally:
                conn.close()
        else:
            logger.error("Connexion à la base de données échouée.")

        return render_template('home/index.html', total_co2=total_co2_kg, image_count=image_count)


    return app
