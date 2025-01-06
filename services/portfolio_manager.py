from services.binance_auth import client
from utils.file_utils import save_data_to_file


def clean_wallet(wallet_info):
    # Remove zero balances
    wallet_info['balances'] = [
        balance for balance in wallet_info['balances']
        if float(balance['free']) > 0.0 or float(balance['locked']) > 0.0
    ]

    # Fetch coin prices
    prices = {price['symbol']: float(price['price']) for price in client.ticker_price()}

    # Add USDT values and handle USDT as a special case
    for balance in wallet_info['balances']:
        if balance['asset'] == "USDT":
            balance['value_in_usdt'] = float(balance['free']) + float(balance['locked'])
        else:
            symbol = f"{balance['asset']}USDT"
            if symbol in prices:
                balance['price_in_usdt'] = prices[symbol]
                balance['value_in_usdt'] = float(balance['free']) * balance['price_in_usdt'] + float(
                    balance['locked']) * balance['price_in_usdt']

    # Sort balances by value and then alphabetically for those with no value
    wallet_info['balances'].sort(
        key=lambda balance: (-balance.get('value_in_usdt', 0), balance['asset'])
    )

    return wallet_info


def fetch_wallet():
    # Fetch wallet info
    wallet_info = client.account()

    # Clean the wallet data
    wallet_info = clean_wallet(wallet_info)

    # Save the wallet data
    save_data_to_file(wallet_info, "wallet_data", "wallet")

    return wallet_info
