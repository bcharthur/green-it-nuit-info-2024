# blueprints/api/script.py
from flask import Flask, jsonify

api_app = Flask(__name__)

@api_app.route('/test')
def test():
    return jsonify({"message": "HelloWorld"})

if __name__ == '__main__':
    api_app.run(host='0.0.0.0', port=5001)  # Port différent pour éviter un conflit
