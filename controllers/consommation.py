# controllers/consommation.py
from flask import Blueprint, render_template
from config.connection_db import get_db_connection

consommation_bp = Blueprint('consommation', __name__)

@consommation_bp.route('/consommation', methods=['GET'])
def consommation():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.id, i.label, s.original_size, s.compressed_size, s.co2_economise
        FROM item i
        INNER JOIN image_stats s ON i.id = s.item_id
    """)
    rows = cursor.fetchall()
    conn.close()

    items_data = [
        {
            "id": row[0],
            "label": row[1],
            "original_size": row[2],
            "compressed_size": row[3],
            "co2_economise": row[4]
        }
        for row in rows
    ]

    return render_template('consommation/index.html', items=items_data)
