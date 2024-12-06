# controllers/items_api.py
from flask import Blueprint, jsonify, request
from config.connection_db import get_db_connection
from PIL import Image
from io import BytesIO

items_api_bp = Blueprint('items_api', __name__)

@items_api_bp.route('/items', methods=['GET'])
def get_items():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, label, original_image FROM item")
    rows = cursor.fetchall()
    conn.close()

    items = []
    for row in rows:
        item_id, label, original_image = row
        has_image = (original_image is not None)
        items.append({"id": item_id, "label": label, "has_image": has_image})

    return jsonify(items=items), 200

@items_api_bp.route('/items', methods=['POST'])
def add_item():
    label = request.form.get('label')
    file = request.files.get('image')

    if not label:
        return jsonify({"msg": "Label is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    if file:
        # Récupération de l'image originale
        original_bytes = file.read()
        original_size = len(original_bytes)

        image = Image.open(BytesIO(original_bytes))
        # Conversion en RGB si RGBA
        if image.mode == "RGBA":
            image = image.convert("RGB")

        # Compression de l'image
        compressed_buffer = BytesIO()
        image.save(compressed_buffer, format="JPEG", quality=50)
        compressed_bytes = compressed_buffer.getvalue()
        compressed_size = len(compressed_bytes)

        # Calcul du CO2 économisé
        co2_economise = (original_size - compressed_size) * 0.0001

        # Insertion de l'item et récupération de son ID
        cursor.execute(
            "INSERT INTO item (label, original_image, compressed_image) OUTPUT inserted.id VALUES (?, ?, ?)",
            (label, original_bytes, compressed_bytes)
        )
        row = cursor.fetchone()

        if row is None or row[0] is None:
            conn.rollback()
            conn.close()
            return jsonify({"msg": "Error retrieving item_id"}), 500

        item_id = row[0]

        # Insertion des stats
        cursor.execute(
            "INSERT INTO image_stats (item_id, original_size, compressed_size, co2_economise) VALUES (?, ?, ?, ?)",
            (item_id, original_size, compressed_size, co2_economise)
        )

        conn.commit()
        conn.close()

        return jsonify({
            "msg": "Item created with image",
            "original_size": original_size,
            "compressed_size": compressed_size,
            "co2_economise": co2_economise
        }), 201
    else:
        # Pas d'image
        cursor.execute("INSERT INTO item (label) VALUES (?)", (label,))
        conn.commit()
        conn.close()

        return jsonify({"msg": "Item created"}), 201

@items_api_bp.route('/items/<int:item_id>', methods=['PUT'])
def edit_item(item_id):
    data = request.get_json()
    label = data.get('label')
    if not label:
        return jsonify({"msg": "Label is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE item SET label = ? WHERE id = ?", (label, item_id))
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({"msg": "Item not found"}), 404
    conn.commit()
    conn.close()

    return jsonify({"msg": "Item updated"}), 200

@items_api_bp.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM item WHERE id = ?", (item_id,))
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({"msg": "Item not found"}), 404
    conn.commit()
    conn.close()

    return jsonify({"msg": "Item deleted"}), 200

@items_api_bp.route('/items/<int:item_id>/original_image', methods=['GET'])
def get_original_image(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT original_image FROM item WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    conn.close()

    if not row or not row[0]:
        return jsonify({"msg": "No image found"}), 404

    original_bytes = row[0]
    from flask import send_file
    image_io = BytesIO(original_bytes)
    response = send_file(image_io, mimetype='image/jpeg', as_attachment=False, download_name=f"original_{item_id}.jpg")
    response.direct_passthrough = False
    return response
