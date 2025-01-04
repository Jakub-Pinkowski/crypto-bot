from binance_auth import client

# Number of items to display
NUM_PRICES_TO_DISPLAY = 15

if __name__ == "__main__":
    # Fetch exchange information (to filter only symbols that are 'TRADING')
    exchange_info = client.exchange_info()

    # Extract all symbols that are actively trading
    active_symbols = {symbol['symbol'] for symbol in exchange_info['symbols'] if symbol['status'] == 'TRADING'}

    # Fetch current market prices
    prices = client.ticker_price()
    print("Current Prices (Only TRADING):")
    trading_prices = [price for price in prices if price['symbol'] in active_symbols]
    for price in trading_prices[:NUM_PRICES_TO_DISPLAY]:  # Print the first NUM_PRICES_TO_DISPLAY symbols
        print(f"Symbol: {price['symbol']}, Price: {price['price']}")

    # Fetch 24h market statistics
    stats = client.ticker_24hr()
    print("\n24h Market Statistics (Only TRADING):")
    trading_stats = [stat for stat in stats if stat['symbol'] in active_symbols]
    for stat in trading_stats[:NUM_PRICES_TO_DISPLAY]:  # Print the first NUM_PRICES_TO_DISPLAY symbols
        symbol = stat["symbol"]
        price_change_percent = stat["priceChangePercent"]
        volume = stat["volume"]
        print(f"Symbol: {symbol}, 24h Change: {price_change_percent}%, Volume: {volume}")
