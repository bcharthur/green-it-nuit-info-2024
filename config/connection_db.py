import pyodbc
import logging
from config.settings import DB_SERVER, DB_NAME, DB_USER, DB_PASSWORD

logger = logging.getLogger(__name__)

def get_db_connection():
    try:
        conn = pyodbc.connect(
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={DB_SERVER};'
            f'DATABASE={DB_NAME};'
            f'UID={DB_USER};'
            f'PWD={DB_PASSWORD};'
            'Trusted_Connection=no;'
        )
        logger.info("Connexion à la base de données réussie!")
        return conn
    except Exception as e:
        logger.error("Erreur de connexion à la base de données: %s", e)
        return None
