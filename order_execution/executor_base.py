from utils.file_utils import save_data_to_file, load_config_values

config = load_config_values("ORDER_VALUE")

def check_coin_balance(wallet_balance, coin):
    for asset in wallet_balance:
        if asset['asset'] == coin:
            return asset  # Return the full asset details
    return None

def buy_coin_with_usdt(coin_to_buy, amount_to_use):

    # TODO: Replace this with API call or actual selling logic
    print(f"Executing buy order: Buy {amount_to_use} USDT worth of {coin_to_buy}.")
    return

def sell_coin_for_usdt(coin_to_sell, wallet_balance, amount_to_use):
    # Find the coin_to_sell in the wallet
    coin_balance = check_coin_balance(wallet_balance, coin_to_sell)

    if not coin_balance:
        print(f"{coin_to_sell} not found in wallet. Cannot sell.")
        return

    # Extract the free balance and its value in USDT
    free_balance = coin_balance['free']
    value_in_usdt = coin_balance.get('value_in_usdt', 0)  # Total value in USDT equivalent

    # Calculate the amount to sell
    if value_in_usdt >= amount_to_use:
        # Sell exactly amount_to_use worth
        print(f"Selling {amount_to_use} USDT worth of {coin_to_sell}.")
        amount_of_coin = amount_to_use / coin_balance['price_in_usdt']  # Convert USDT to coin amount
    else:
        # Sell whatever balance is available
        print(f"Insufficient balance. Selling entire {free_balance} of {coin_to_sell} (worth {value_in_usdt} USDT).")
        amount_of_coin = free_balance

    # TODO: Replace this with API call or actual selling logic
    print(f"Executing sell order: Sell {amount_of_coin} {coin_to_sell}.")
    return amount_of_coin

def make_transactions(coins_to_trade, wallet_balance):
    # Amount to use for buying the new coin (in USDT)
    amount_to_use = config['ORDER_VALUE']
    print(f"Amount to use for buying: {amount_to_use}")

    # Extract relevant coins and their scores from the input
    coin_to_buy = coins_to_trade['coin_to_buy']['coin']
    coin_to_sell = coins_to_trade['coin_to_sell']['coin']

    # Check if enough USDT is available in the wallet
    usdt_balance_details = check_coin_balance(wallet_balance, 'USDT')
    usdt_balance = usdt_balance_details['free'] if usdt_balance_details else 0

    print(f"Current USDT balance: {usdt_balance}")

    # If there's enough USDT, proceed to buy the coin_to_buy
    if usdt_balance >= amount_to_use:
        buy_coin_with_usdt(coin_to_buy, amount_to_use)
    else:
        sell_coin_for_usdt(coin_to_sell, wallet_balance, amount_to_use)
