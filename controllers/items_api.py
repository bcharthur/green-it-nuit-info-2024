# controllers/items_api.py
from flask import Blueprint, jsonify, request
from config.connection_db import get_db_connection
from PIL import Image
from io import BytesIO
import hashlib

items_api_bp = Blueprint('items_api', __name__)

@items_api_bp.route('/items', methods=['GET'])
def get_items():
    conn = get_db_connection()
    cursor = conn.cursor()
    # On récupère les items avec le label et le fait qu'ils aient une image ou non
    # Comme désormais l'image est dans la table images, on teste si image_id est non NULL
    cursor.execute("SELECT id, label, image_id FROM item")
    rows = cursor.fetchall()
    conn.close()

    items = []
    for row in rows:
        item_id, label, image_id = row
        has_image = (image_id is not None)
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
        # Lire l'image originale
        original_bytes = file.read()
        original_size = len(original_bytes)

        # Ouvrir l'image avec Pillow
        image = Image.open(BytesIO(original_bytes))
        # Conversion RGBA -> RGB si nécessaire
        if image.mode == "RGBA":
            image = image.convert("RGB")

        # Compression
        compressed_buffer = BytesIO()
        image.save(compressed_buffer, format="JPEG", quality=50)
        compressed_bytes = compressed_buffer.getvalue()
        compressed_size = len(compressed_bytes)

        # Calcul du CO2 économisé (exemple arbitraire)
        co2_economise = (original_size - compressed_size) * 0.0001

        # Calcul du hash de l'image originale
        hash_value = hashlib.sha256(original_bytes).hexdigest()

        # Vérifier si l'image existe déjà
        cursor.execute("SELECT id FROM images WHERE hash = ?", (hash_value,))
        row = cursor.fetchone()
        if row:
            # L'image existe déjà, on récupère son id
            image_id = row[0]
        else:
            # Insérer la nouvelle image
            cursor.execute(
                "INSERT INTO images (hash, original_image, compressed_image) OUTPUT inserted.id VALUES (?, ?, ?)",
                (hash_value, original_bytes, compressed_bytes)
            )
            new_row = cursor.fetchone()
            if not new_row:
                conn.rollback()
                conn.close()
                return jsonify({"msg": "Error inserting image"}), 500
            image_id = new_row[0]

        # Insérer l'item en le liant à image_id
        cursor.execute(
            "INSERT INTO item (label, image_id) OUTPUT inserted.id VALUES (?, ?)",
            (label, image_id)
        )
        item_row = cursor.fetchone()
        if not item_row:
            conn.rollback()
            conn.close()
            return jsonify({"msg": "Error inserting item"}), 500
        item_id = item_row[0]

        # Insérer les stats
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
        # Pas d'image, insertion simple
        cursor.execute("INSERT INTO item (label) OUTPUT inserted.id VALUES (?)", (label,))
        item_row = cursor.fetchone()
        if not item_row:
            conn.rollback()
            conn.close()
            return jsonify({"msg": "Error inserting item without image"}), 500
        item_id = item_row[0]
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
    # Récupérer image_id de l'item
    cursor.execute("SELECT image_id FROM item WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    if not row or not row[0]:
        conn.close()
        return jsonify({"msg": "Item or image not found"}), 404
    image_id = row[0]

    # Récupérer l'image originale depuis images
    cursor.execute("SELECT original_image FROM images WHERE id = ?", (image_id,))
    image_row = cursor.fetchone()
    conn.close()

    if not image_row or not image_row[0]:
        return jsonify({"msg": "No image found"}), 404

    original_bytes = image_row[0]
    from flask import send_file
    image_io = BytesIO(original_bytes)
    response = send_file(image_io, mimetype='image/jpeg', as_attachment=False, download_name=f"original_{item_id}.jpg")
    response.direct_passthrough = False
    return response
