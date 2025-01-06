from services.binance_auth import client
from utils.file_utils import save_data_to_file

def fetch_wallet():
    # Fetch wallet info
    wallet_info = client.account()

    # Filter out balances where both `free` and `locked` are '0.0'
    wallet_info['balances'] = [
        balance for balance in wallet_info['balances']
        if float(balance['free']) > 0.0 or float(balance['locked']) > 0.0
    ]

    save_data_to_file(wallet_info, "wallet_data", "wallet")

    return wallet_info