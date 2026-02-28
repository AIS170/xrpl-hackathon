# portfolio_setup.py
from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
from xrpl.transaction import submit_and_wait
from xrpl.models.transactions import TrustSet, Payment
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.wallet import generate_faucet_wallet
from xrpl.models.requests import GatewayBalances

# XRPL Testnet URL
TESTNET_URL = "https://s.altnet.rippletest.net:51234"
client = JsonRpcClient(TESTNET_URL)


def create_test_wallet():
    """
    Generates and funds a Testnet wallet with XRP from Faucet.
    """
    wallet = generate_faucet_wallet(client)
    print("✔️ Created Testnet Wallet:", wallet.classic_address)
    print("   Seed:", wallet.seed)
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
    Sends issued currency from issuer wallet → portfolio wallet.
    """
    wallet = Wallet.from_seed(from_seed)
    payment_tx = Payment(
        account=wallet.classic_address,
        destination=to_address,
        amount=IssuedCurrencyAmount(
            currency=currency,
            issuer=issuer_address,
            value=str(amount)
        ),
    )
    response = submit_and_wait(payment_tx, client, wallet)
    return response


def setup_demo_portfolio():
    """
    Initializes portfolio and issuer wallets and funds portfolio with demo tokens.
    """
    print("⚡ Setting up demo portfolio on XRPL Testnet...")

    # 1️⃣ Create portfolio wallet
    portfolio_wallet = create_test_wallet()

    # 2️⃣ Create separate issuer wallets for BTC and AUD
    btc_issuer_wallet = create_test_wallet()
    aud_issuer_wallet = create_test_wallet()

    # 3️⃣ Create trust lines (portfolio → issuers)
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

    # 4️⃣ Send demo tokens from issuer → portfolio
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

    # 5️⃣ Return portfolio information including issuer addresses
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

    print("✔️ Demo portfolio setup complete!")
    return portfolio_data


def get_portfolio_balances(portfolio_wallet_address, issuer_addresses):
    """
    Returns balances of XRP and all issued currencies for the portfolio wallet.
    """
    # 1. Get XRP balance
    from xrpl.models.requests import AccountInfo
    account_info = client.request(AccountInfo(
        account=portfolio_wallet_address,
        ledger_index="validated",
        strict=True
    )).result
    xrp_balance = int(account_info['account_data']['Balance']) / 1_000_000  # convert drops → XRP

    # 2. Get issued currency balances using GatewayBalances
    gb_response = client.request(GatewayBalances(
        account=portfolio_wallet_address,
        ledger_index="validated",
        hotwallet=list(issuer_addresses.values())
    )).result

    issued_balances = {}
    balances_data = gb_response.get("balances", {})
    for name, addr in issuer_addresses.items():
        tokens = balances_data.get(addr, {})
        issued_balances[name] = sum(float(v['value']) for v in tokens.values()) if tokens else 0.0

    # Combine XRP + issued currencies
    balances = {"XRP": xrp_balance}
    balances.update(issued_balances)
    return balances


if __name__ == "__main__":
    setup_demo_portfolio()