import math
from services.binance_auth import client
from services.portfolio_manager import fetch_wallet_balance
from utils.file_utils import save_data_to_file, load_config_values

config = load_config_values("ORDER_VALUE")

def check_coin_balance(wallet_balance, coin):
    for asset in wallet_balance:
        if asset['asset'] == coin:
            return float(asset['free'])
    raise ValueError(f"{coin} notfound in wallet.")


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

    # Calculate quantity
    quantity = amount_to_use / current_price

    # Ensure quantity is not below the minimum allowed quantity
    if quantity < min_qty:
        quantity = min_qty

    # Round to the nearest step size
    quantity = math.floor(quantity / step_size) * step_size

    # Validate quantity
    if not (min_qty <= quantity <= max_qty):
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

        # Calculate the quantity to sell using the helper function
        quantity = extract_and_calculate_quantity(coin_to_sell, trading_pair, coins_data, amount_to_use)

        # Ensure quantity does not exceed available balance
        if quantity > coin_balance:
            print(f"Insufficient {coin_to_sell} balance. Selling entire available balance: {coin_balance}")
            quantity = coin_balance

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

def make_transactions(coin_analysis, wallet_balance, coins_data):
    # Amount to use for buying a new coin (in USDT)
    amount_to_use = config['ORDER_VALUE']

    # Perform SELL actions
    for analysis in coin_analysis:
        coin = analysis['coin']
        action = analysis['action']

        if action == 'SELL':
            print(f"Attempting to sell {coin}")
            try:
                sell_coin_for_usdt(coin, amount_to_use, coins_data, wallet_balance)
            except Exception as e:
                print(f"Error during selling {coin}: {str(e)}")

    # Fetch new wallet info
    updated_wallet_balance = fetch_wallet_balance()
    usdt_balance = check_coin_balance(updated_wallet_balance, 'USDT')
    print(f"Updated USDT balance: {usdt_balance}")

    # Perform BUY actions if sufficient USDT balance
    for analysis in coin_analysis:
        coin = analysis['coin']
        action = analysis['action']

        if action == 'BUY':
            print(f"Attempting to buy {coin}")
            # Ensure there's enough USDT to proceed with buying
            if usdt_balance >= amount_to_use:
                try:
                    buy_coin_with_usdt(coin, amount_to_use, coins_data)
                except Exception as e:
                    print(f"Error during buying {coin}: {str(e)}")
            else:
                print(f"Insufficient USDT balance to buy {coin}. Available: {usdt_balance}, Required: {amount_to_use}")