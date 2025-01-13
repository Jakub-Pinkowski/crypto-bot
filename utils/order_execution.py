def check_coin_balance(wallet_balance, coin):
    for asset in wallet_balance:
        if asset['asset'] == coin:
            return float(asset['free'])
    raise ValueError(f"{coin} notfound in wallet.")

def round_quantity_to_step_size(quantity, step_size):
    # Validate that step_size is positive
    if step_size < 0:
        raise ValueError("Step size must be greater than or equal to 0.")

    # Calculate the number of decimal places in step_size and round the quality accordingly
    step_size_str = str(step_size)
    decimal_places = len(step_size_str.split('.')[1]) if '.' in step_size_str else 0
    quantity = round(quantity / step_size) * step_size

    # Round the quantity to match the precision of step_size, need this to get around floating-point precision
    quantity = round(quantity, decimal_places)

    return quantity

def extract_filter_parameters(filters):
    lot_size_filter = next((f for f in filters if f['filterType'] == 'LOT_SIZE'), None)
    notional_filter = next((f for f in filters if f['filterType'] == 'NOTIONAL'), None)

    if not lot_size_filter:
        raise ValueError("'LOT_SIZE' filter not found")
    if not notional_filter:
        raise ValueError("'NOTIONAL' filter not found")

    min_qty = float(lot_size_filter['minQty'])
    max_qty = float(lot_size_filter['maxQty'])
    step_size = float(lot_size_filter['stepSize'])
    min_notional = float(notional_filter['minNotional'])

    return min_qty, max_qty, step_size, min_notional

def validate_quantity(quantity, min_qty, max_qty, current_price, min_notional):
    total_value = quantity * current_price
    if quantity < min_qty:
        raise ValueError(f"Quantity {quantity} is below the minimum allowed quantity of {min_qty}")
    if quantity > max_qty:
        raise ValueError(f"Quantity {quantity} exceeds the maximum allowed quantity of {max_qty}")
    if total_value < min_notional:
        raise ValueError(f"Total value {total_value} is below the minimum notional value of {min_notional}")
