# controllers/auth.py
from flask import Blueprint, jsonify, request, render_template, flash, redirect, url_for
from flask_login import login_user, logout_user, current_user
from flask_jwt_extended import create_access_token
from models.user import User, users
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # Lors d'un accès direct (GET), on affiche le formulaire HTML
        return render_template('api/login.html')

    # Si on arrive ici, c’est un POST (formulaire envoyé)
    username = request.form.get('username')
    password = request.form.get('password')

    if username in users and users[username]['password'] == password:
        user = User(username)
        login_user(user)
        logger.info(f"Utilisateur {username} connecté avec succès")

        # Récupérer l'URL de destination (paramètre 'next')
        next_url = request.args.get('next') or url_for('home')

        # Redirection vers la page demandée (par exemple /api)
        return redirect(next_url)
    else:
        logger.warning(f"Tentative de connexion échouée pour l'utilisateur {username}")
        flash("Identifiants invalides", "danger")
        return render_template('api/login.html')

@auth_bp.route('/logout', methods=['GET'])
def logout():
    if current_user.is_authenticated:
        logger.info(f"Utilisateur {current_user.id} s'est déconnecté")
        logout_user()
    return jsonify({"msg": "Déconnecté"}), 200
