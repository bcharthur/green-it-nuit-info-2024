from flask import Blueprint, render_template
from flask_login import login_required, current_user
from config.connection_db import get_db_connection
import logging

logger = logging.getLogger(__name__)
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/api')
@login_required
def api_dashboard():
    logger.info(f"Utilisateur {current_user.id} accède à /api")
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT userVar, method, timestampVar, endpoint, json_response FROM [db_green].[dbo].[api_logs]")
        logs = cursor.fetchall()
        logs_data = [
            {
                "user": log[0],
                "method": log[1],
                "timestamp": log[2].strftime("%Y-%m-%d %H:%M:%S"),
                "endpoint": log[3],
                "json_response": log[4]
            } for log in logs
        ]

        return render_template('api/index.html', api_logs=logs_data)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des logs pour le dashboard : {e}")
        return "Erreur lors de la récupération des logs.", 500
    finally:
        if conn:
            conn.close()
