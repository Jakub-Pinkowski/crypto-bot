from services.binance_auth import client
from services.portfolio_manager import fetch_wallet_balance
from utils.file_utils import save_data_to_file, load_config_values
from utils.order_execution import check_coin_balance, extract_filter_parameters, round_quantity_to_step_size, validate_quantity

config = load_config_values("ORDER_VALUE", "STOP_LOSS_DELTA", "TAKE_PROFIT_DELTA")

def extract_and_calculate_quantity(coin, trading_pair, coins_data, amount_to_use, coin_balance=None):
    # Fetch the current price
    current_price = float(client.ticker_price(symbol=trading_pair)['price'])

    # Extract filters for the trading pair
    filters = coins_data[coin]['pair_metadata'][trading_pair]['filters']
    min_qty, max_qty, step_size, min_notional = extract_filter_parameters(filters)

    # Calculate the desired quantity using the amount_to_use and current price
    desired_quantity = amount_to_use / current_price
    quantity = round_quantity_to_step_size(desired_quantity, step_size)

    # Validate the calculated quantity
    validate_quantity(quantity, min_qty, max_qty, current_price, min_notional)

    # If coin_balance is provided (selling a coin), adjust the quantity accordingly
    if coin_balance is not None:
        if quantity < coin_balance:
            return quantity
        else:
            coin_balance = round_quantity_to_step_size(coin_balance, step_size)

            # Validate the adjusted coin balance
            validate_quantity(coin_balance, min_qty, max_qty, current_price, min_notional)

            return coin_balance

    # If coin_balance is not provided, simply return the calculated quantity
    return quantity

def buy_coin_with_usdt(coin_to_buy, amount_to_use, coins_data):
    # Define the trading pair
    trading_pair = f"{coin_to_buy}USDT"

    # Define the trading delta for the attached selling order
    stop_loss_delta = config['STOP_LOSS_DELTA']
    take_profit_delta = config['TAKE_PROFIT_DELTA']

    try:
        # Calculate, process and validate quantity
        quantity = extract_and_calculate_quantity(
            coin=coin_to_buy,
            trading_pair=trading_pair,
            coins_data=coins_data,
            amount_to_use=amount_to_use,
        )

        # NOTE: Remove the test part whenever needed
        # Place a buy order
        buy_order = client.new_order_test(
            symbol=trading_pair,
            side='BUY',
            type='MARKET',
            quantity=quantity
        )

        # Print the summary
        print(f"Bought {quantity} of {coin_to_buy} for {amount_to_use} USDT.")

        # Save the transaction details to a file
        save_data_to_file(buy_order, "transactions", "transaction")

        # TODO: Add tests to this function all all dependent on it
        # TODO: Add a config whether we attach the selling orders or not
        # TODO: Test the values of price, stopPrice for each function

        # Calculate the take profit and stop loss prices based on current market price
        current_price = float(client.ticker_price(symbol=trading_pair)['price'])
        take_profit_price = current_price * (1 + take_profit_delta / 100)
        stop_loss_price = current_price * (1 - stop_loss_delta / 100)

        # Place the take-profit order (take-profit-limit)
        take_profit_order = client.new_order_test(
            symbol=trading_pair,
            side='SELL',
            type='TAKE_PROFIT_LIMIT',
            quantity=quantity,
            price=str(round(take_profit_price, 2)),  # Round to 2 decimals
            stopPrice=str(round(take_profit_price, 2)),  # Trigger at the same price
            timeInForce = 'GTC'  # Adding the 'timeInForce' parameter
        )
        print(f"Take Profit Order Placed: {take_profit_order}")
        save_data_to_file(take_profit_order, "transactions", "take_profit_order")

        # Place the stop-loss order (stop-loss-limit)
        stop_loss_order = client.new_order_test(
            symbol=trading_pair,
            side='SELL',
            type='STOP_LOSS_LIMIT',
            quantity=quantity,
            price=str(round(stop_loss_price, 2)),  # Round to 2 decimals
            stopPrice=str(round(stop_loss_price, 2)),  # Trigger at the same price
            timeInForce='GTC'  # Adding the 'timeInForce' parameter
        )

        print(f"Stop Loss Order Placed: {stop_loss_order}")
        save_data_to_file(stop_loss_order, "transactions", "stop_loss_order")

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