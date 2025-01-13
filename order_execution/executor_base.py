import math
from services.binance_auth import client
from services.portfolio_manager import fetch_wallet_balance
from utils.file_utils import save_data_to_file, load_config_values

config = load_config_values("ORDER_VALUE", "TRAILING_DELTA")

def check_coin_balance(wallet_balance, coin):
    for asset in wallet_balance:
        if asset['asset'] == coin:
            return float(asset['free'])
    raise ValueError(f"{coin} notfound in wallet.")


def round_quantity_to_step_size(quantity, step_size):
    # Calculate the number of decimal places in step_size and round the quality accordingly
    step_size_str = str(step_size)
    decimal_places = len(step_size_str.split('.')[1]) if '.' in step_size_str else 0
    quantity = round(quantity / step_size) * step_size

    # Round the quantity to match the precision of step_size, need this to get around floating-point precision
    quantity = round(quantity, decimal_places)

    return quantity

def extract_and_calculate_quantity(coin, trading_pair, coins_data, amount_to_use, coin_balance):
    # Fetch the current price
    current_price = float(client.ticker_price(symbol=trading_pair)['price'])

    # Extract LOT_SIZE filter
    filters = coins_data[coin]['pair_metadata'][trading_pair]['filters']
    lot_size_filter = next((f for f in filters if f['filterType'] == 'LOT_SIZE'), None)
    if not lot_size_filter:
        raise ValueError(f"LOT_SIZE filter not found for trading pair {trading_pair}")

    # Extract NOTIONAL filter
    notional_filter = next((f for f in filters if f['filterType'] == 'NOTIONAL'), None)
    if not notional_filter:
        raise ValueError(f"NOTIONAL filter not found for trading pair {trading_pair}")


    min_qty = float(lot_size_filter['minQty'])
    max_qty = float(lot_size_filter['maxQty'])
    step_size = float(lot_size_filter['stepSize'])
    min_notional = float(notional_filter['minNotional'])

    # Calculate the desired quantity using the amount_to_use and current price
    desired_quantity = amount_to_use / current_price
    quantity = round_quantity_to_step_size(desired_quantity, step_size)

    # Ensure the quantity is within the allowed range and meets the min_notional condition
    if quantity < min_qty:
        raise ValueError(f"Calculated quantity {quantity} is below the minimum allowed quantity of {min_qty}")
    if quantity > max_qty:
        raise ValueError(f"Calculated quantity {quantity} exceeds the maximum allowed quantity of {max_qty}")
    if quantity * current_price < min_notional:
        raise ValueError(f"Calculated quantity is below the minimum notional value of {min_notional}")

    if quantity < coin_balance:
        return quantity
    else:
        raise ValueError(f"Insufficient balance for {coin}. Available: {coin_balance}, Required: {quantity}")


def buy_coin_with_usdt(coin_to_buy, amount_to_use, coins_data):
    # Define the trading pair
    trading_pair = f"{coin_to_buy}USDT"

    # Define the trading delta for the attached selling order
    trailing_delta = config['TRAILING_DELTA']

    try:
        # Calculate, process and validate quantity
        quantity = extract_and_calculate_quantity(coin_to_buy, trading_pair, coins_data, amount_to_use)

        # NOTE: Remove the test part whenever needed
        # Place a buy order
        buy_order = client.new_order.test(
            symbol=trading_pair,
            side='BUY',
            type='MARKET',
            quantity=quantity
        )

        # Print the summary
        print(f"Bought {quantity} of {coin_to_buy} for {amount_to_use} USDT.")

        # Save the transaction details to a file
        save_data_to_file(buy_order, "transactions", "transaction")

        # Optionally, place a trailing sell order
        if trailing_delta:
            # NOTE: Remove the test part whenever needed
            # Place a trailing stop market sell order
            trailing_order = client.new_order.test(
                symbol=trading_pair,
                side='SELL',
                type='TRAILING_STOP_MARKET',
                quantity=quantity,
                trailingDelta=trailing_delta
            )
            print(f"Trailing Sell Order Successful: {trailing_order}")
            save_data_to_file(trailing_order, "transactions", "trailing_sell_order")

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
        quantity = extract_and_calculate_quantity(
            coin=coin_to_sell,
            trading_pair=trading_pair,
            coins_data=coins_data,
            amount_to_use=amount_to_use,
            coin_balance=coin_balance
        )

        # Place a sell order
        order = client.new_order_test(
            symbol=trading_pair,
            side='SELL',
            type='MARKET',
            quantity=quantity
        )

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

    for analysis in coin_analysis:
        coin = analysis['coin']
        action = analysis['action']

        if action == 'SELL':
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