from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from models.user import User, users
import logging

auth_api_bp = Blueprint('auth_api', __name__)
logger = logging.getLogger(__name__)

@auth_api_bp.route('/auth/login', methods=['POST'])
def api_login():
    username = request.json.get('username') or request.form.get('username')
    password = request.json.get('password') or request.form.get('password')

    if username in users and users[username]['password'] == password:
        # Pas de login_user ici, car c'est une authentification purement API
        logger.info(f"Utilisateur {username} connecté (API) avec succès")
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        logger.warning(f"Tentative de connexion (API) échouée pour l'utilisateur {username}")
        return jsonify({"msg": "Invalid credentials"}), 401
