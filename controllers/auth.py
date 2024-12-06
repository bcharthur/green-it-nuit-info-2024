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
        return render_template('api/login.html')

    username = request.form.get('username')
    password = request.form.get('password')

    if username in users and users[username]['password'] == password:
        user = User(username)
        login_user(user)
        logger.info(f"Utilisateur {username} connecté avec succès")

        # Rediriger directement vers /api après connexion réussie
        return redirect(url_for('dashboard.api_dashboard'))
    else:
        logger.warning(f"Tentative de connexion échouée pour l'utilisateur {username}")
        flash("Identifiants invalides", "danger")
        return render_template('api/login.html')

@auth_bp.route('/logout', methods=['GET'])
def logout():
    if current_user.is_authenticated:
        logger.info(f"Utilisateur {current_user.id} s'est déconnecté")
        logout_user()
        flash("admin déconnecté", "success")  # Message flash

    # Redirection vers la page d'accueil
    return redirect(url_for('home'))
