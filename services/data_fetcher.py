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

def filter_potential_coins(all_symbols_data):
    """
    Filters potential coins based on the following criteria:
    - Significant price change (high volatility): Abs(priceChangePercent) > price_change_threshold
    - Moderate trading volume: min_quote_volume < quoteVolume < max_quote_volume
    - High price range volatility: (highPrice - lowPrice) / lowPrice > price_range_volatility_threshold
    - Excludes popular coins like BTCUSDT and ETHUSDT

    Parameters:
        all_symbols_data (dict): Dictionary containing exchange_info, active_symbols, prices, and stats.

    Returns:
        dict: Dictionary of filtered coins with relevant data.
    """

    # Define filter thresholds
    price_change_threshold = 5.0  # Minimum percentage price change (absolute)
    price_range_volatility_threshold = 0.10  # Minimum range volatility (15%)

    # Extract relevant data from the input
    stats = all_symbols_data["stats"]
    active_symbols = all_symbols_data["active_symbols"]

    # Define filters
    filtered_coins = {
        stat['symbol']: {
            "priceChangePercent": float(stat['priceChangePercent']),
            "quoteVolume": float(stat['quoteVolume']),
            "priceRangeVolatility": (float(stat['highPrice']) - float(stat['lowPrice'])) / float(stat['lowPrice']),
        }
        for stat in stats
        if stat['symbol'] in active_symbols and
           abs(float(stat['priceChangePercent'])) > price_change_threshold and
           (float(stat['highPrice']) - float(stat['lowPrice'])) / float(
            stat['lowPrice']) > price_range_volatility_threshold
    }

    return filtered_coins


if __name__ == "__main__":
    # Fetch all general symbol data
    all_symbols_data = fetch_all_symbols_data()

    # Filter potential coins
    potential_coins = filter_potential_coins(all_symbols_data)

    # Example output
    print("Potential Coins for Further Analysis:")
    for symbol, data in potential_coins.items():
        print(f"{symbol} -> {data}")

