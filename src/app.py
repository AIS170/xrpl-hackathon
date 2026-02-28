from flask import Flask
from routes import register_routes
from flask_cors import CORS
from portfolio_setup import get_portfolio_balances, setup_demo_portfolio

app = Flask(__name__)
CORS(app)
register_routes(app)

# app.py snippet
if __name__ == "__main__":
    print("⚡ Setting up demo portfolio on XRPL Testnet...")
    portfolio_data = setup_demo_portfolio()
    
    # Now we just pass the address; it finds BTC, AUD, and anything else automatically
    wallet_address = portfolio_data["portfolio_wallet"]["xrpl_address"]
    balances = get_portfolio_balances(wallet_address)

    print("💰 Current Portfolio Balances:")
    for currency, amount in balances.items():
        print(f"  {currency}: {amount}")

    app.run(host="0.0.0.0", port=5000, debug=True)