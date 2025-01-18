from services.binance_auth import client
from services.wallet_info import fetch_wallet_balance
from utils.file_utils import save_data_to_file, load_config_values
from utils.order_execution import check_coin_balance, extract_filter_parameters, round_number, format_price, validate_quantity

config = load_config_values("ORDER_VALUE", "STOP_LOSS_DELTA", "TAKE_PROFIT_DELTA")

def calculate_quantity(current_price, filter_params, amount_to_use, coin_balance=None):
    # Extract the variables from filters
    min_qty = filter_params['lot_size']['min_qty']
    max_qty = filter_params['lot_size']['max_qty']
    step_size = filter_params['lot_size']['step_size']
    min_notional = filter_params['notional']['min_notional']

    # Calculate the desired quantity using the amount_to_use and current price
    desired_quantity = amount_to_use / current_price

    quantity = round_number(desired_quantity, step_size)

    # Validate the calculated quantity
    validate_quantity(quantity, min_qty, max_qty, current_price, min_notional)

    # If coin_balance is provided (selling a coin), adjust the quantity accordingly
    if coin_balance is not None:
        if quantity < coin_balance:
            return quantity
        else:
            coin_balance = round_number(coin_balance, step_size)

            # Validate the adjusted coin balance
            validate_quantity(coin_balance, min_qty, max_qty, current_price, min_notional)

            return coin_balance

    # If coin_balance is not provided, simply return the calculated quantity
    return quantity

def calculate_prices(current_price, take_profit_delta, stop_loss_delta, filter_params):
    # Extract the variables from filters
    min_price = filter_params['price']['min_price']
    max_price = filter_params['price']['max_price']
    tick_size = filter_params['price']['price_tick_size']

    # Calculate initial prices
    take_profit_price = current_price * (1 + take_profit_delta / 10000)
    stop_loss_price = current_price * (1 - stop_loss_delta / 10000)

    # Ensure prices are within the min and max price bounds
    take_profit_price = max(min_price, min(max_price, take_profit_price))
    stop_loss_price = max(min_price, min(max_price, stop_loss_price))

    # Round the prices
    take_profit_price = round_number(take_profit_price, tick_size)
    stop_loss_price = round_number(stop_loss_price, tick_size)

    # Format the prices
    take_profit_price = format_price(take_profit_price, tick_size)
    stop_loss_price = format_price(stop_loss_price, tick_size)

    return take_profit_price, stop_loss_price

def validate_trailing_deltas(filter_params):
    # Define the trading delta for the attached selling order
    take_profit_delta = config['TAKE_PROFIT_DELTA']
    stop_loss_delta = config['STOP_LOSS_DELTA']

    min_trailing_above_delta = filter_params['trailing_delta']['min_trailing_above_delta']
    max_trailing_above_delta = filter_params['trailing_delta']['max_trailing_above_delta']
    min_trailing_below_delta = filter_params['trailing_delta']['min_trailing_below_delta']
    max_trailing_below_delta = filter_params['trailing_delta']['max_trailing_below_delta']

    if take_profit_delta < min_trailing_above_delta:
        take_profit_delta = min_trailing_above_delta

    if take_profit_delta > max_trailing_above_delta:
        take_profit_delta = max_trailing_above_delta

    if stop_loss_delta < min_trailing_below_delta:
        stop_loss_delta = min_trailing_below_delta

    if stop_loss_delta > max_trailing_below_delta:
        stop_loss_delta = max_trailing_below_delta

    return take_profit_delta, stop_loss_delta

def buy_coin_with_usdt(coin_to_buy, amount_to_use, coins_data):
    # TODO: Refactor, clean and test all of this once it's working

    # Define the trading pair
    trading_pair = f"{coin_to_buy}USDT"

    # Extract filters for the trading pair
    filters = coins_data[coin_to_buy]['pair_metadata'][trading_pair]['filters']
    filter_params = extract_filter_parameters(filters)

    # Get the current price from the market
    current_price = float(client.ticker_price(symbol=trading_pair)['price'])

    # Calculate, process and validate quantity
    quantity = calculate_quantity(
        current_price=current_price,
        filter_params=filter_params,
        amount_to_use=amount_to_use
    )

    # Calculate, process and validate trailing delta
    take_profit_trailing_delta, stop_loss_trailing_delta = validate_trailing_deltas(
        filter_params=filter_params
    )

    # Calculate, process and validate price
    take_profit_price, stop_loss_price = calculate_prices(
        current_price=current_price,
        take_profit_delta=take_profit_trailing_delta,
        stop_loss_delta=stop_loss_trailing_delta,
        filter_params=filter_params
    )

    try:
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
        save_data_to_file(buy_order, "transactions", "buy_order")

        # TODO: Add tests to this function all all dependent on it
        # TODO: Add a config whether we attach the selling orders or not
        # TODO: Test the values of price, stopPrice for each function
        # https://developers.binance.com/docs/binance-spot-api-docs/faqs/trailing-stop-faq#trailing-stop-order-scenarios

        # TODO: Take profit and stop loss should cancel each other whenever executed

        # Place the take-profit order (take-profit-limit)
        take_profit_order = client.new_order_test(
            symbol=trading_pair,
            side='SELL',
            type='TAKE_PROFIT_LIMIT',
            quantity=quantity,
            price=take_profit_price,
            stopPrice=take_profit_price,
            trailingDelta=take_profit_trailing_delta,
            timeInForce = 'GTC'
        )
        print(f"Take Profit Order Placed: {take_profit_order}")
        save_data_to_file(take_profit_order, "transactions", "take_profit_order")

        # Place the stop-loss order (stop-loss-limit)
        stop_loss_order = client.new_order_test(
            symbol=trading_pair,
            side='SELL',
            type='STOP_LOSS_LIMIT',
            quantity=quantity,
            price=stop_loss_price,
            stopPrice=stop_loss_price,
            trailingDelta=stop_loss_trailing_delta,
            timeInForce='GTC'
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

        # Extract filters for the trading pair
        filters = coins_data[coin_to_sell]['pair_metadata'][trading_pair]['filters']
        filter_params = extract_filter_parameters(filters)

        # Get the current price from the market
        current_price = float(client.ticker_price(symbol=trading_pair)['price'])

        # Find the coin_to_sell in the wallet
        coin_balance = check_coin_balance(wallet_balance, coin_to_sell)

        # Calculate, process and validate quantity
        quantity = calculate_quantity(
            current_price=current_price,
            filter_params=filter_params,
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
        save_data_to_file(order, "transactions", "sell_order")
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