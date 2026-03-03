from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
from xrpl.transaction import submit_and_wait
from xrpl.models.transactions import TrustSet, Payment
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.wallet import generate_faucet_wallet
from xrpl.models.requests import GatewayBalances
from xrpl.models.requests import AccountInfo, AccountLines

import json
import os
from datetime import datetime

# XRPL Testnet URL
TESTNET_URL = "https://s.altnet.rippletest.net:51234"
client = JsonRpcClient(TESTNET_URL)


def create_test_wallet():
    """
    Generates and funds a Testnet wallet with XRP from Faucet.
    """
    wallet = generate_faucet_wallet(client)
    print("Created Testnet Wallet:", wallet.classic_address)
    print("Seed:", wallet.seed)
    return wallet


def create_trust_line(account_seed, issuer_address, currency, limit="1000"):
    """
    Creates a trust line to allow the portfolio wallet to receive issued tokens.
    """
    wallet = Wallet.from_seed(account_seed)
    trust_tx = TrustSet(
        account=wallet.classic_address,
        limit_amount=IssuedCurrencyAmount(
            currency=currency,
            issuer=issuer_address,
            value=str(limit)
        )
    )
    response = submit_and_wait(trust_tx, client, wallet)
    return response


def send_issued_token(from_seed, to_address, issuer_address, currency, amount):
    """
    Sends issued currency from issuer wallet to portfolio wallet or vice versa.
    """
    wallet = Wallet.from_seed(from_seed)
    issued_currency_amount = IssuedCurrencyAmount(
        currency=currency,
        issuer=issuer_address,
        value=str(amount)
    )

    payment_tx = Payment(
        account=wallet.classic_address,
        destination=to_address,
        amount=issued_currency_amount,
        send_max=issued_currency_amount,
        flags=131072
    )

    response = submit_and_wait(payment_tx, client, wallet)

    if "tesSUCCESS" not in response.result.get("meta", {}).get("TransactionResult", ""):
        raise Exception(f"Transaction failed: {response.result.get('meta', {}).get('TransactionResult')}")

    return response


def setup_demo_portfolio():
    """
    Initializes portfolio and issuer wallets and funds portfolio with demo tokens.
    """
    print("Setting up demo portfolio on XRPL Testnet")

    portfolio_wallet = create_test_wallet()

    btc_issuer_wallet = create_test_wallet()
    aud_issuer_wallet = create_test_wallet()

    create_trust_line(
        account_seed=portfolio_wallet.seed,
        issuer_address=btc_issuer_wallet.classic_address,
        currency="BTC",
        limit="100"
    )
    create_trust_line(
        account_seed=portfolio_wallet.seed,
        issuer_address=aud_issuer_wallet.classic_address,
        currency="AUD",
        limit="10000"
    )

    send_issued_token(
        from_seed=btc_issuer_wallet.seed,
        to_address=portfolio_wallet.classic_address,
        issuer_address=btc_issuer_wallet.classic_address,
        currency="BTC",
        amount="5"
    )
    send_issued_token(
        from_seed=aud_issuer_wallet.seed,
        to_address=portfolio_wallet.classic_address,
        issuer_address=aud_issuer_wallet.classic_address,
        currency="AUD",
        amount="5000"
    )

    portfolio_data = {
        "portfolio_wallet": {
            "xrpl_address": portfolio_wallet.classic_address,
            "seed": portfolio_wallet.seed
        },
        "issuers": {
            "BTC": {
                "xrpl_address": btc_issuer_wallet.classic_address,
                "seed": btc_issuer_wallet.seed
            },
            "AUD": {
                "xrpl_address": aud_issuer_wallet.classic_address,
                "seed": aud_issuer_wallet.seed
            }
        },
        "tokens": {
            "BTC": 5,
            "AUD": 5000
        },
        "history": []
    }

    print("Demo portfolio setup complete!")
    return portfolio_data


def get_portfolio_balances(portfolio_wallet_address):
    """
    Dynamically fetches all balances (XRP + all Trust Lines) for a wallet.
    """
    # Get XRP balance
    account_info = client.request(AccountInfo(
        account=portfolio_wallet_address,
        ledger_index="validated"
    )).result

    # Convert drops to XRP (1 XRP = 1,000,000 drops)
    xrp_balance = int(account_info['account_data']['Balance']) / 1_000_000

    # Get all issued currency balances (Trust Lines)
    lines_response = client.request(AccountLines(
        account=portfolio_wallet_address,
        ledger_index="validated"
    )).result

    balances = {"XRP": xrp_balance}

    # Iterate through all trust lines and add them to the balances dict
    for line in lines_response.get("lines", []):
        currency = line["currency"]
        balance = float(line["balance"])
        balances[currency] = balance

    return balances


def execute_request(transactions):
    """
    Simulates executing a list of community-approved transactions
    by updating the local wallet.json balances directly.
    """
    if not os.path.exists("wallet.json"):
        raise Exception("Wallet not initialized")

    with open("wallet.json", "r") as f:
        wallet_data = json.load(f)

    tokens = wallet_data.get("tokens", {})

    if "history" not in wallet_data:
        wallet_data["history"] = []

    for t in transactions:
        t_type = t.get("type", "BUY")
        asset = t.get("asset", "BTC")
        amount = float(t.get("amount", 0))
        impact_aud = float(t.get("impactAud", 0))

        if t_type == "BUY":
            # Deduct AUD, add asset
            tokens["AUD"] = tokens.get("AUD", 0) - impact_aud
            tokens[asset] = tokens.get(asset, 0) + amount
            print(f"BUY: -{impact_aud} AUD, +{amount} {asset}")

        elif t_type == "SELL":
            # Deduct asset, add AUD
            tokens[asset] = tokens.get(asset, 0) - amount
            tokens["AUD"] = tokens.get("AUD", 0) + impact_aud
            print(f"SELL: -{amount} {asset}, +{impact_aud} AUD")

        wallet_data["history"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "type": t_type,
            "asset": asset,
            "amount": amount,
            "impactAud": impact_aud
        })

    wallet_data["tokens"] = tokens

    with open("wallet.json", "w") as f:
        json.dump(wallet_data, f, indent=4)

    print(f"Updated balances: {tokens}")
    return True


if __name__ == "__main__":
    setup_demo_portfolio()