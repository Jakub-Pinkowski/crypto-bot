from binance_auth import client

# Threshold for minimum percentage increase
PRICE_INCREASE_THRESHOLD = 5.0  # 5% increase

if __name__ == "__main__":
    # Fetch exchange information
    exchange_info = client.exchange_info()

    # Extract all symbols that are actively trading
    active_symbols = {symbol['symbol'] for symbol in exchange_info['symbols'] if symbol['status'] == 'TRADING'}

    # Fetch current market prices and filter out non-trading symbols
    prices = client.ticker_price()
    trading_prices = [price for price in prices if price['symbol'] in active_symbols]

    # Fetch 24h market statistics
    stats = client.ticker_24hr()
    trading_stats = [stat for stat in stats if stat['symbol'] in active_symbols]