from services.binance_auth import client
from utils.file_utils import save_data_to_file

def extract_balance(wallet_info):
    wallet_balance = []

    # Remove zero balances
    wallet_info['balances'] = [
        balance for balance in wallet_info['balances']
        if float(balance['free']) > 0.0 or float(balance['locked']) > 0.0
    ]

    # Fetch coin prices
    prices = {price['symbol']: float(price['price']) for price in client.ticker_price()}

    # Add USDT values and handle USDT as a special case
    for balance in wallet_info['balances']:
        symbol = f"{balance['asset']}USDT"
        if symbol in prices or balance['asset'] == "USDT":  # Ensure USDT exists in symbol or is USDT
            asset_info = {
                'asset': balance['asset'],
                'free': float(balance['free']),
                'locked': float(balance['locked']),
            }
            if balance['asset'] == "USDT":
                asset_info['value_in_usdt'] = asset_info['free'] + asset_info['locked']
            else:
                asset_info['price_in_usdt'] = prices[symbol]
                asset_info['value_in_usdt'] = asset_info['free'] * asset_info['price_in_usdt'] + \
                                              asset_info['locked'] * asset_info['price_in_usdt']

            wallet_balance.append(asset_info)

    # Sort balances by value and then alphabetically for those with no value
    wallet_balance.sort(
        key=lambda balance: (-balance.get('value_in_usdt', 0), balance['asset'])
    )

    return wallet_balance

def fetch_wallet_balance():
    # Fetch wallet info
    wallet_info = client.account()

    # Extract the wallet's balance
    wallet_balance = extract_balance(wallet_info)

    # Save the wallet data
    save_data_to_file(wallet_balance, "wallet_data", "wallet_balance")

    return wallet_info
