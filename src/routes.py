# routes.py
from flask import request, jsonify
from auth_utils import authenticate_user


def register_routes(app):
    @app.route('/')
    def index():
        return "Stablecoin API is Live!"

    @app.route('/api/login', methods=['POST'])
    def login():
        data = request.json
        id_token = data.get('token')

        if not id_token:
            return jsonify(
                {"status": "error", "message": "No token provided"}
            ), 400

        try:
            user_data = authenticate_user(id_token)
            return jsonify({"status": "success", "user": user_data}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 401

    @app.route('/api/logout', methods=['POST'])
    def logout():
        # MVP: Logout can just be frontend removing token
        return jsonify({"status": "success", "message": "Logged out"}), 200