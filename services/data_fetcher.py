from binance_auth import client

def fetch_all_symbols_data():
    """
    Fetches general data for all symbols:
    - Exchange information (active symbols, metadata)
    - Current market prices
    - 24-hour market statistics
    Returns a dictionary with the fetched data.
    """
    # Fetch exchange information (metadata for symbols)
    exchange_info = client.exchange_info()
    active_symbols = {symbol['symbol'] for symbol in exchange_info['symbols'] if symbol['status'] == 'TRADING'}

    # Fetch current market prices (real-time data)
    prices = client.ticker_price()
    trading_prices = [price for price in prices if price['symbol'] in active_symbols]

    # Fetch 24-hour market statistics
    stats = client.ticker_24hr()
    trading_stats = [stat for stat in stats if stat['symbol'] in active_symbols]

    # Return all data in a dictionary
    return {
        "exchange_info": exchange_info,  # Full exchange metadata
        "active_symbols": active_symbols,  # Set of active trading pairs
        "prices": trading_prices,  # Filtered price data
        "stats": trading_stats,  # Filtered 24-hour stats
    }


if __name__ == "__main__":
    # Fetch all general symbol data
    all_symbols_data = fetch_all_symbols_data()

    print(all_symbols_data)