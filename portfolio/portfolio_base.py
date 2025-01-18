import csv
from services.binance_auth import client
from utils.file_utils import save_data_to_file, load_data_from_file


# NOTE: The whole file is not being used yet
def get_wallet_info():
    # Fetch wallet info
    wallet_info = client.account()

    wallet_balance = []

    # Remove zero balances
    wallet_info['balances'] = [
        balance for balance in wallet_info['balances']
        if float(balance['free']) > 0.0 or float(balance['locked']) > 0.0
    ]

    # Fetch coin prices
    prices = {price['symbol']: float(price['price']) for price in client.ticker_price()}

    # Process balances
    for balance in wallet_info['balances']:
        symbol = f"{balance['asset']}USDT"
        if symbol in prices or balance['asset'] == "USDT":  # Ensure USDT exists in symbol or is USDT
            asset_info = {
                'asset': balance['asset'],
                'free': float(balance['free']),
                'locked': float(balance['locked']),
            }
            if balance['asset'] == "USDT":
                asset_info['value_in_usdt'] = asset_info['free'] + asset_info['locked']
            else:
                asset_info['price_in_usdt'] = prices[symbol]
                asset_info['value_in_usdt'] = asset_info['free'] * asset_info['price_in_usdt'] + \
                                              asset_info['locked'] * asset_info['price_in_usdt']

            wallet_balance.append(asset_info)

    # Sort balances by value in descending order
    wallet_balance.sort(
        key=lambda balance: -balance['value_in_usdt']
    )

    # Calculate the total portfolio value in USDT
    total_value_in_usdt = sum(item['value_in_usdt'] for item in wallet_balance)

    # Add percentage field
    for item in wallet_balance:
        item['percentage'] = round((item['value_in_usdt'] / total_value_in_usdt) * 100, 2)

    return wallet_balance, total_value_in_usdt


def process_changes(current_data, previous_data=None):
    if not previous_data:
        # If no previous data, initialize changes to None
        for item in current_data:
            item['value_change'] = None
            item['volume_change'] = None
        return current_data

    # Map previous data for easier lookup
    prev_map = {item['asset']: item for item in previous_data}

    # Calculate changes
    for item in current_data:
        prev_item = prev_map.get(item['asset'])
        if prev_item:
            # Value change
            item['value_change'] = round(
                item['value_in_usdt'] - prev_item['value_in_usdt'], 2
            )
            item['value_change_percentage'] = round(
                (item['value_change'] / prev_item['value_in_usdt']) * 100, 2
            ) if prev_item['value_in_usdt'] > 0 else None

            # Volume change
            current_volume = item['free'] + item['locked']
            prev_volume = prev_item['free'] + prev_item['locked']
            item['volume_change'] = round(current_volume - prev_volume, 2)
        else:
            # No previous record
            item['value_change'] = None
            item['volume_change'] = None

    return current_data


def export_to_csv(data, filename="wallet_data.csv"):
    # Define the CSV file's header
    headers = ['Asset', 'Free', 'Locked', 'Price in USDT', 'Value in USDT', 'Percentage', 'Value Change', 'Volume Change',
               'Value Change Percentage']

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(headers)

        # Write the data rows
        for item in data:
            writer.writerow([
                item.get('asset'),
                item.get('free'),
                item.get('locked'),
                item.get('price_in_usdt'),
                item.get('value_in_usdt'),
                item.get('percentage'),
                item.get('value_change'),
                item.get('volume_change'),
                item.get('value_change_percentage')
            ])

    print(f"Data successfully exported to {filename}")


def main():
    # Load previous data
    previous_data = load_data_from_file("portfolio", "wallet_data")

    # Get current wallet info
    current_data, total_value_in_usdt = get_wallet_info()

    # Process changes
    current_data = process_changes(current_data, previous_data)

    # Save current data for future comparisons
    save_data_to_file(current_data, "portfolio", "wallet_data")

    # Save the data to scv
    export_to_csv(current_data)


if __name__ == "__main__":
    main()
