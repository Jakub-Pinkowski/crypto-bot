from services.binance_auth import client
from utils.file_utils import save_data_to_file

def fetch_wallet():
    import logging
    # Fetch wallet info
    wallet_info = client.account()

    # Filter out balances where both `free` and `locked` are '0.0'
    wallet_info['balances'] = [
        balance for balance in wallet_info['balances']
        if float(balance['free']) > 0.0 or float(balance['locked']) > 0.0
    ]

    prices = {price['symbol']: float(price['price']) for price in client.ticker_price()}
    print(f"Prices fetched.")

    # Add USDT prices only for relevant balances
    for balance in wallet_info['balances']:
        # Special case: if the asset is USDT
        if balance['asset'] == "USDT":
            balance['value_in_usdt'] = float(balance['free']) + float(balance['locked'])
        else:
            # For other assets, calculate based on their USDT price
            symbol = f"{balance['asset']}USDT"
            if symbol in prices:
                balance['price_in_usdt'] = prices[symbol]
                balance['value_in_usdt'] = float(balance['free']) * balance['price_in_usdt'] + float(
                    balance['locked']) * \
                                           balance['price_in_usdt']
            else:
                # Skip balances that cannot be converted to USDT
                continue

    # Sort balances by value and then by alphabetical order
    wallet_info['balances'].sort(
        key=lambda balance: (-balance.get('value_in_usdt', 0), balance['asset'])
    )

    save_data_to_file(wallet_info, "wallet_data", "wallet")

    return wallet_info