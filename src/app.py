# app.py
import os
import json
from flask import Flask
from routes import register_routes
from flask_cors import CORS
from portfolio_setup import get_portfolio_balances, setup_demo_portfolio

app = Flask(__name__)
CORS(app)
register_routes(app)

WALLET_FILE = "wallet.json"

def init_portfolio():
    """Loads existing wallet or creates a new one and saves to JSON."""
    if os.path.exists(WALLET_FILE):
        print("📁 Loading existing portfolio from wallet.json...")
        with open(WALLET_FILE, "r") as f:
            return json.load(f)
    else:
        print("⚡ Setting up new demo portfolio on XRPL Testnet...")
        portfolio_data = setup_demo_portfolio()
        with open(WALLET_FILE, "w") as f:
            json.dump(portfolio_data, f, indent=4)
        print("✅ Saved new portfolio to wallet.json!")
        return portfolio_data

if __name__ == "__main__":
    # Removed the WERKZEUG_RUN_MAIN check completely!
    portfolio_data = init_portfolio()
    wallet_address = portfolio_data["portfolio_wallet"]["xrpl_address"]
    
    balances = get_portfolio_balances(wallet_address)
    print("💰 Current Portfolio Balances:")
    for currency, amount in balances.items():
        print(f"  {currency}: {amount}")

    # You can safely turn debug=True back on for development, 
    # or leave it as False. The file check handles the logic now!
    app.run(host="0.0.0.0", port=5002, debug=False)