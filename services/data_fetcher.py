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
    Filters potential symbols based on the following criteria:
    - Significant price change (high volatility): Abs(priceChangePercent) > price_change_threshold
    - High price range volatility: (highPrice - lowPrice) / lowPrice > price_range_volatility_threshold

    Then extracts a robust set of unique assets (coins) from the filtered symbols.

    Parameters:
        all_symbols_data (dict): Dictionary containing exchange_info, active_symbols, prices, and stats.

    Returns:
        set: Set of unique assets (coins) from the filtered symbols.
    """

    # Define filter thresholds
    price_change_threshold = 5.0  # Minimum percentage price change (absolute)
    price_range_volatility_threshold = 0.05  # Minimum range volatility in %

    # Extract relevant data from input
    exchange_info = all_symbols_data["exchange_info"]["symbols"]
    active_symbols = all_symbols_data["active_symbols"]
    stats = all_symbols_data["stats"]

    # Map symbols to their respective base and quote assets using exchange_info
    symbol_mapping = {
        symbol_data['symbol']: {
            'baseAsset': symbol_data['baseAsset'],
            'quoteAsset': symbol_data['quoteAsset']
        }
        for symbol_data in exchange_info
    }

    # Filter symbols based on criteria
    filtered_symbols = [
        stat['symbol']
        for stat in stats
        if stat['symbol'] in active_symbols and
           abs(float(stat['priceChangePercent'])) > price_change_threshold and
           (float(stat['highPrice']) - float(stat['lowPrice'])) / float(
            stat['lowPrice']) > price_range_volatility_threshold
    ]

    # Extract unique base assets using the mapping from Step 1
    potential_coins = {symbol_mapping[symbol]['baseAsset'] for symbol in filtered_symbols}

    return potential_coins


if __name__ == "__main__":
    # Example usage
    all_symbols_data = fetch_all_symbols_data()

    # Step 1: Filter potential coins
    potential_coins = filter_potential_coins(all_symbols_data)

    # Step 2: Output list of unique assets
    print("Unique Assets for Further Analysis:")
    print(potential_coins)
