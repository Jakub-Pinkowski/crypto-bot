import json
import os
from datetime import datetime
from services.binance_auth import client

def get_coins_data():
    """
    Main function to fetch and prepare coins data.
    It performs the following steps:
    1. Fetch general symbols data.
    2. Filter for potential coins based on criteria.
    3. Fetch market data for filtered coins.
    4. Save the coins data to a file for later use.

    Returns:
        dict: A dictionary containing detailed data for all filtered coins.
    """
    # Step 1: Fetch general symbols data
    all_symbols_data = fetch_all_symbols_data()

    # Step 2: Filter for potential coins
    potential_coins = filter_potential_coins(all_symbols_data)

    # Step 3: Fetch detailed data for filtered coins
    coins_data = fetch_coins_data(all_symbols_data, potential_coins)

    # Step 4: Save coins data to a file
    save_coins_data_to_file(coins_data)

    # Return the coins data
    return coins_data


def fetch_all_symbols_data():
    """
    Fetches general data for all symbols:
    - Exchange information (active symbols, metadata)
    - Current market prices
    - 24-hour market statistics

    Returns:
        dict: Dictionary containing exchange_info, active_symbols, prices, and stats.
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
        set: Set of unique coins from the filtered symbols.
    """

    # Define filter thresholds
    price_change_threshold = 5.0  # Minimum percentage price change (absolute)
    price_range_volatility_threshold = 0.01  # Minimum range volatility in %

    # Extract relevant data from input
    symbols = all_symbols_data["exchange_info"]["symbols"]
    active_symbols = all_symbols_data["active_symbols"]
    stats = all_symbols_data["stats"]

    # Map symbols to their respective base and quote assets using symbols
    symbol_mapping = {
        symbol_data['symbol']: {
            'baseAsset': symbol_data['baseAsset'],
            'quoteAsset': symbol_data['quoteAsset']
        }
        for symbol_data in symbols
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

    # Extract unique coins from the symbols
    potential_coins = {symbol_mapping[symbol]['baseAsset'] for symbol in filtered_symbols}

    return potential_coins

def fetch_coins_data(all_symbols_data, potential_coins):
    """
    Fetches data for each coin in the potential_coins set, including:
    - Active trading pairings for each coin
    - Order book data for active trading pairs
    - Recent trades for each active trading pair
    - Candlestick data (last 24 hours with 1-hour intervals)
    - Aggregated trades for each active trading pair

    Parameters:
        all_symbols_data (dict): Dictionary containing exchange information and active symbols.
        potential_coins (set): Set of potential coins to fetch data for.

    Returns:
        dict: A dictionary containing detailed data for each coin.
              Each coin is mapped to its trading data, including:
              - "pairings": List of active trading pairs for the coin.
              - "order_books": Order book data for all active trading pairs.
              - "recent_trades": Recent trades information for each trading pair.
              - "candlesticks": Last 24 candlesticks (1-hour interval) for each pair.
              - "aggregated_trades": Aggregated trade data for each pair.
    """

    coins_data = {}

    # Extract data from all_symbols_data
    symbols = all_symbols_data["exchange_info"]["symbols"]
    active_symbols = all_symbols_data["active_symbols"]
    prices = {price["symbol"]: float(price["price"]) for price in all_symbols_data["prices"]}
    stats = {stat["symbol"]: stat for stat in all_symbols_data["stats"] if stat["symbol"] in active_symbols}

    for coin in potential_coins:
        pairings = [symbol for symbol in symbols if symbol['baseAsset'] == coin or symbol['quoteAsset'] == coin]
        trading_pairs = [pair['symbol'] for pair in pairings if pair['symbol'] in active_symbols]

        # Collect metadata for each pair
        pair_metadata = {
            pair['symbol']: {
                "baseAsset": pair["baseAsset"],
                "quoteAsset": pair["quoteAsset"],
                "pricePrecision": pair["baseAssetPrecision"],
                "qtyPrecision": pair["quotePrecision"],
                "filters": pair["filters"],
            }
            for pair in pairings if pair["symbol"] in active_symbols
        }

        # Initialize data collectors
        order_books = {}
        recent_trades = {}
        candlestick_data = {}
        aggregated_trades = {}

        # Collect data for each pairing
        for pair in trading_pairs:
            # Order book
            order_books[pair] = client.depth(symbol=pair, limit=100)

            # Recent trades
            recent_trades[pair] = client.trades(symbol=pair, limit=100)

            # Candlestick data (last 24 1-hour candles)
            candlestick_data[pair] = client.klines(symbol=pair, interval='1h', limit=24)

            # Aggregated trades
            aggregated_trades[pair] = client.agg_trades(symbol=pair, limit=100)

        # Store everything in the coin data
        coins_data[coin] = {
            "pairings": trading_pairs,  # Active trading pairs
            "pair_metadata": pair_metadata,  # Metadata for each pair
            "real_time_prices": {  # Latest prices for active pairs
                pair: prices.get(pair, None) for pair in trading_pairs
            },
            "market_stats": {  # 24-hour market stats
                pair: stats.get(pair, {}) for pair in trading_pairs
            },
            "order_books": order_books,  # Order book data
            "recent_trades": recent_trades,  # Recent trades
            "candlesticks": candlestick_data,  # Candlesticks (OHLC data)
            "aggregated_trades": aggregated_trades,  # Aggregated trades
        }

    return coins_data

def save_coins_data_to_file(coins_data, filename=None):
    """
    Saves coins_data to a JSON file in the market_data folder.

    Parameters:
        coins_data (dict): The data to be saved.
        filename (str, optional): File name for the saved data. Uses timestamp by default.

    Returns:
        Nothing
    """
    # Default file name with timestamp if none is provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"coins_data_{timestamp}.json"

    # Ensure the market_data folder exists
    base_dir = os.path.dirname(os.path.dirname(__file__))  # Navigate to project root
    directory = os.path.join(base_dir, "data", "market_data")
    os.makedirs(directory, exist_ok=True)  # Ensure target directory exists

    # Save the data as JSON
    file_path = os.path.join(directory, filename)
    with open(file_path, "w") as file:
        json.dump(coins_data, file, indent=4)

    print(f"Coins data saved to {file_path}")
