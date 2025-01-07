import math
from services.binance_auth import client
from utils.file_utils import save_data_to_file, load_config_values

config = load_config_values("ORDER_VALUE")

def check_coin_balance(wallet_balance, coin):
    for asset in wallet_balance:
        if asset['asset'] == coin:
            return asset  # Return the full asset details
    return None

def buy_coin_with_usdt(coin_to_buy, amount_to_use, coins_data):
    try:
        # Define the trading pair
        trading_pair = f"{coin_to_buy}USDT"

        # Fetch the current price of the coin
        current_price = float(client.ticker_price(symbol=trading_pair)['price'])

        # Extract LOT_SIZE filter directly
        filters = coins_data[coin_to_buy]['pair_metadata'][trading_pair]['filters']
        lot_size_filter = next((f for f in filters if f['filterType'] == 'LOT_SIZE'), None)
        if not lot_size_filter:
            raise ValueError(f"LOT_SIZE filter not found for trading pair {trading_pair}")

        min_qty = float(lot_size_filter['minQty'])
        max_qty = float(lot_size_filter['maxQty'])
        step_size = float(lot_size_filter['stepSize'])
        print(f"step_size: {step_size}")

        # Calculate quantity and adjust to step size
        quantity = amount_to_use / current_price
        quantity = math.floor(quantity / step_size) * step_size
        print(f"Quantity: {quantity}")

        # Validate quantity
        if not (min_qty <= float(quantity) <= max_qty):
            raise ValueError(f"Quantity {quantity} out of range: [{min_qty}, {max_qty}]")

        # Place an order
        # order = client.new_order(
        #     symbol=trading_pair,
        #     side='BUY',
        #     type='MARKET',
        #     quantity=quantity
        # )

        # Simulate success
        print(f"Bought {quantity} of {coin_to_buy} for {amount_to_use} USDT at {current_price} USDT per unit.")

        # Save the transaction details to a file
        save_data_to_file(order, "transactions", "transaction")
    except Exception as e:
        # Handle and log any errors during the buy transaction
        print(f"An error occurred while trying to buy {coin_to_buy}: {e}")

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

def make_transactions(coins_to_trade, wallet_balance, coins_data):
    # Amount to use for buying the new coin (in USDT)
    amount_to_use = config['ORDER_VALUE']

    # Extract relevant coins and their scores from the input
    coin_to_buy = coins_to_trade['coin_to_buy']['coin']
    coin_to_sell = coins_to_trade['coin_to_sell']['coin']

    # Check if enough USDT is available in the wallet
    usdt_balance_details = check_coin_balance(wallet_balance, 'USDT')
    usdt_balance = usdt_balance_details['free'] if usdt_balance_details else 0

    # If there's enough USDT, proceed to buy the coin_to_buy
    if usdt_balance >= amount_to_use:
        buy_coin_with_usdt(coin_to_buy, amount_to_use, coins_data)
    else:
        sell_coin_for_usdt(coin_to_sell, wallet_balance, amount_to_use)
