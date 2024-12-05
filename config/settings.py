import os
from dotenv import load_dotenv

load_dotenv()  # Charge les variables d'environnement depuis .env

# Clés secrètes et config
SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'change_me')
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'another_super_secret_key')

# Base de données
DB_SERVER = os.getenv('DB_SERVER', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'db_green')
DB_USER = os.getenv('DB_USER', 'sa')
DB_PASSWORD = os.getenv('DB_PASSWORD', '123456789')

# Autres configurations
DEBUG = True
