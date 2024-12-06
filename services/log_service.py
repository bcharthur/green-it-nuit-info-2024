import logging
from datetime import datetime
from config.connection_db import get_db_connection

logger = logging.getLogger(__name__)

def enregistrer_log(user_id, method, endpoint, json_response):
    """
    Enregistre un log dans la base de données.
    """
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            logger.error("Échec de la connexion à la base de données lors de l'enregistrement du log.")
            return

        cursor = conn.cursor()
        current_timestamp = datetime.now()

        # Log dans la console pour diagnostic
        logger.info(f"Log : Utilisateur {user_id} a appelé l'endpoint {endpoint} avec la méthode {method}")
        logger.info(f"Réponse JSON : {json_response}")

        sql = """
               INSERT INTO [db_green].[dbo].[api_logs] (userVar, methodVar, timestampVar, endpoint, json_response)
               VALUES (?, ?, ?, ?, ?)
           """
        cursor.execute(sql, (user_id, method, current_timestamp, endpoint, json_response))

        conn.commit()
        logger.info(f"Log inséré dans la base de données pour l'endpoint {endpoint}")

    except Exception as e:
        logger.error(f"Erreur lors de l'insertion du log dans la base de données : {e}")
    finally:
        if conn:
            conn.close()
