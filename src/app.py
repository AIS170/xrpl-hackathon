from flask import Flask
from routes import register_routes
from flask_cors import CORS
from portfolio_setup import get_portfolio_balances, setup_demo_portfolio

app = Flask(__name__)
CORS(app)
register_routes(app)

if __name__ == "__main__":
    # Run this once when the app starts
    print("⚡ Setting up demo portfolio on XRPL Testnet...")
    portfolio_data = setup_demo_portfolio()
    print("✅ Portfolio setup complete:")
    print(portfolio_data)

    # Extract issuer addresses from portfolio_data
    issuer_addresses = {
        k: v["xrpl_address"]  # v is the issuer wallet info
        for k, v in portfolio_data["issuers"].items()
    }

    # Get balances (XRP + issued tokens)
    balances = get_portfolio_balances(
        portfolio_data["portfolio_wallet"]["xrpl_address"], issuer_addresses
    )

    print("💰 Portfolio balances:")
    print(balances)

    app.run(host="0.0.0.0", port=5002, debug=True)