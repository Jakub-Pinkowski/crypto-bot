import math
from services.binance_auth import client
from utils.file_utils import save_data_to_file, load_config_values

config = load_config_values("ORDER_VALUE")

def check_coin_balance(wallet_balance, coin):
    for asset in wallet_balance:
        if asset['asset'] == coin:
            asset['free'] = float(asset['free'])  # Ensure 'free' balance is a float
            asset['locked'] = float(asset['locked'])  # Ensure 'locked' balance is a float
            asset['total'] = asset['free'] + asset['locked']  # Compute total balance
            return asset
    raise ValueError(f"{coin} not found in wallet.")

def extract_and_calculate_quantity(coin_to_buy, trading_pair, coins_data, amount_to_use):
    # Fetch the current price
    current_price = float(client.ticker_price(symbol=trading_pair)['price'])

    # Extract LOT_SIZE filter
    filters = coins_data[coin_to_buy]['pair_metadata'][trading_pair]['filters']
    lot_size_filter = next((f for f in filters if f['filterType'] == 'LOT_SIZE'), None)
    if not lot_size_filter:
        raise ValueError(f"LOT_SIZE filter not found for trading pair {trading_pair}")

    min_qty = float(lot_size_filter['minQty'])
    max_qty = float(lot_size_filter['maxQty'])
    step_size = float(lot_size_filter['stepSize'])

    # Calculate quantity and adjust to step size
    quantity = amount_to_use / current_price
    quantity = math.floor(quantity / step_size) * step_size

    # Validate quantity
    if not (min_qty <= float(quantity) <= max_qty):
        raise ValueError(f"Quantity {quantity} out of range: [{min_qty}, {max_qty}]")

    return quantity

def buy_coin_with_usdt(coin_to_buy, amount_to_use, coins_data):
    try:
        # Define the trading pair
        trading_pair = f"{coin_to_buy}USDT"

        # Calculate, process and validate quantity
        quantity = extract_and_calculate_quantity(coin_to_buy, trading_pair, coins_data, amount_to_use)
        print(f"Validated Quantity: {quantity}")

        # Place an order
        # order = client.new_order(
        #     symbol=trading_pair,
        #     side='BUY',
        #     type='MARKET',
        #     quantity=quantity
        # )

        # Print the summary
        print(f"Bought {quantity} of {coin_to_buy} for {amount_to_use} USDT.")

        # Save the transaction details to a file
        save_data_to_file(order, "transactions", "transaction")
    except Exception as e:
        # Handle and log any errors during the buy transaction
        print(f"An error occurred while trying to buy {coin_to_buy}: {e}")

def sell_coin_for_usdt(coin_to_sell, amount_to_use, coins_data, wallet_balance):
    try:
        # Define the trading pair
        trading_pair = f"{coin_to_sell}USDT"

        # Find the coin_to_sell in the wallet
        coin_balance = check_coin_balance(wallet_balance, coin_to_sell)
        free_balance = coin_balance['free']

        # Calculate the quantity to sell using the helper function
        quantity = extract_and_calculate_quantity(coin_to_sell, trading_pair, coins_data, amount_to_use)

        # Ensure quantity does not exceed available balance
        if quantity > free_balance:
            print(f"Insufficient {coin_to_sell} balance. Selling entire available balance: {free_balance}")
            quantity = free_balance

        print(f"Validated selling quantity: {quantity}")

        # Place a sell order
        # order = client.new_order(
        #     symbol=trading_pair,
        #     side='SELL',
        #     type='MARKET',
        #     quantity=quantity
        # )

        # Print the summary
        print(f"Sold {quantity} of {coin_to_sell} for USDT")

        # Save the transaction details to a file
        save_data_to_file(order, "transactions", "transaction")
    except Exception as e:
        # Handle and log any errors during the sell transaction
        print(f"An error occurred while trying to sell {coin_to_sell}: {e}")


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
        sell_coin_for_usdt(coin_to_sell, amount_to_use, coins_data, wallet_balance)
