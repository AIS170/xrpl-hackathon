# routes.py
from flask import request, jsonify
from auth_utils import authenticate_user
from portfolio_setup import get_portfolio_balances

def register_routes(app):
    
    @app.route('/')
    def index():
        return "Stablecoin API is Live!"

    @app.route('/api/login', methods=['POST'])
    def login():
        """
        Handles Firebase ID token verification and user session/creation.
        """
        data = request.json
        id_token = data.get('token')

        if not id_token:
            return jsonify(
                {"status": "error", "message": "No token provided"}
            ), 400

        try:
            # This utility should verify the token and return user info from Firestore
            user_data = authenticate_user(id_token)
            return jsonify({"status": "success", "user": user_data}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 401

    @app.route('/api/logout', methods=['POST'])
    def logout():
        """
        MVP: Logout is handled by the frontend clearing the local token.
        """
        return jsonify({"status": "success", "message": "Logged out"}), 200

    @app.route('/api/portfolio/<address>', methods=['GET'])
    def get_balances(address):
        """
        Fetches all XRP and Trust Line (Issued Currency) balances for a given XRPL address.
        """
        try:
            # Calls the updated account_lines logic in portfolio_setup.py
            balances = get_portfolio_balances(address)
            return jsonify({
                "status": "success", 
                "address": address,
                "balances": balances
            }), 200
        except Exception as e:
            # Handle cases like invalid address or connection issues
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route('/api/portfolio/demo', methods=['GET'])
    def get_demo_portfolio():
        """
        Optional helper route to quickly get data for a hardcoded demo 
        if you aren't passing the address from the frontend yet.
        """
        # Replace with a real testnet address for testing if needed
        demo_address = "rPT1S77D7GqU7ghM9HKA6QvAb5pXpXpXpX" 
        try:
            balances = get_portfolio_balances(demo_address)
            return jsonify({"status": "success", "balances": balances}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500