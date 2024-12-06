from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from config.connection_db import get_db_connection
import logging

logger = logging.getLogger(__name__)

api_logs_bp = Blueprint('api_logs', __name__)

@api_logs_bp.route('/logs', methods=['GET'])
@jwt_required()  # si vous utilisez JWT
def get_logs():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT userVar, methodVar, timestampVar, endpoint, json_response FROM api_logs")
        logs = cursor.fetchall()

        logs_data = [
            {
                "user": log[0],
                "method": log[1],
                "timestamp": log[2].strftime("%Y-%m-%d %H:%M:%S") if log[2] else None,
                "endpoint": log[3],
                "json_response": log[4]
            }
            for log in logs
        ]

        return jsonify({"logs": logs_data}), 200
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des logs : {e}")
        return jsonify({"msg": "Erreur lors de la récupération des logs"}), 500
    finally:
        if conn:
            conn.close()