# routes.py
from flask import request, jsonify
from firebase_admin import auth
from db import get_or_create_user

def register_routes(app):
    @app.route('/')
    def index():
        return "Stablecoin API is Live!"

    @app.route('/api/login', methods=['POST'])
    def login():
        # 1. Get the token sent from your Frontend (JS)
        data = request.json
        id_token = data.get('token')
        
        try:
            # 2. Verify the token with Firebase
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            email = decoded_token.get('email')
            
            # 3. Get/Create user in our NoSQL Database
            user_data = get_or_create_user(uid, email)
            
            return jsonify({"status": "success", "user": user_data}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 401