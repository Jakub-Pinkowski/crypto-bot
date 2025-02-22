from decimal import Decimal, ROUND_HALF_UP


def check_coin_balance(wallet_balance, coin):
    for asset in wallet_balance:
        if asset['asset'] == coin:
            return float(asset['free'])
    raise ValueError(f"{coin} notfound in wallet.")


def round_number(number, step_size):
    # Convert inputs to Decimal for precision
    number = Decimal(str(number))
    step_size = Decimal(str(step_size))

    # Validate that step_size is positive
    if step_size <= 0:
        raise ValueError("Step size must be greater than 0.")

    # Round the number to the nearest step size
    rounded_number = (number / step_size).quantize(Decimal('1'), rounding=ROUND_HALF_UP) * step_size

    # Round again to match the precision of step_size
    rounded_number = rounded_number.quantize(step_size)

    return float(rounded_number)  # Convert back to float


def format_price(price, tick_size):
    # Convert tick_size to string to determine the number of decimal places
    tick_size_decimal_places = abs(int(Decimal(str(tick_size)).as_tuple().exponent))

    # Format the price with the appropriate number of decimal places
    return f"{price:.{tick_size_decimal_places}f}"


def extract_filter_parameters(filters):
    # Find relevant filters
    price_filter = next((f for f in filters if f['filterType'] == 'PRICE_FILTER'), None)
    lot_size_filter = next((f for f in filters if f['filterType'] == 'LOT_SIZE'), None)
    notional_filter = next((f for f in filters if f['filterType'] == 'NOTIONAL'), None)
    trailing_delta = next((f for f in filters if f['filterType'] == 'TRAILING_DELTA'), None)

    # Check if each filter is found
    if not price_filter:
        raise ValueError("'PRICE_FILTER' filter not found")
    if not lot_size_filter:
        raise ValueError("'LOT_SIZE' filter not found")
    if not notional_filter:
        raise ValueError("'NOTIONAL' filter not found")
    if not trailing_delta:
        raise ValueError("'TRAILING_DELTA' filter not found")

    # Store the values in a dictionary
    filter_params = {
        'price': {
            'min_price': float(price_filter['minPrice']),
            'max_price': float(price_filter['maxPrice']),
            'price_tick_size': float(price_filter['tickSize'])
        },
        'lot_size': {
            'min_qty': float(lot_size_filter['minQty']),
            'max_qty': float(lot_size_filter['maxQty']),
            'step_size': float(lot_size_filter['stepSize'])
        },
        'notional': {
            'min_notional': float(notional_filter['minNotional'])
        },
        'trailing_delta': {
            'min_trailing_above_delta': float(trailing_delta['minTrailingAboveDelta']),
            'max_trailing_above_delta': float(trailing_delta['maxTrailingAboveDelta']),
            'min_trailing_below_delta': float(trailing_delta['minTrailingBelowDelta']),
            'max_trailing_below_delta': float(trailing_delta['maxTrailingBelowDelta'])
        }
    }

    return filter_params


def validate_quantity(quantity, min_qty, max_qty, current_price, min_notional):
    total_value = quantity * current_price
    if quantity < min_qty:
        raise ValueError(f"Quantity {quantity} is below the minimum allowed quantity of {min_qty}")
    if quantity > max_qty:
        raise ValueError(f"Quantity {quantity} exceeds the maximum allowed quantity of {max_qty}")
    if total_value < min_notional:
        raise ValueError(f"Total value {total_value} is below the minimum notional value of {min_notional}")
