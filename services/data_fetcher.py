from services.binance_auth import client
from services.wallet_info import fetch_wallet_balance
from utils.file_utils import save_data_to_file, load_config_values

config = load_config_values("PRICE_CHANGE_THRESHOLD", "PRICE_RANGE_VOLATILITY_THRESHOLD")

def get_coins_data():
    # Fetch general symbols data
    all_symbols_data = fetch_all_symbols_data()

    # Filter for potential coins
    potential_coins = filter_potential_coins(all_symbols_data)
    print(f"Potential coins: {potential_coins}")

    # Fetch my own coins
    wallet_balance = fetch_wallet_balance()
    wallet_coins = {item['asset'] for item in wallet_balance}

    # Combine coins into one variable
    potential_and_wallet_coins = potential_coins.union(wallet_coins)

    # Fetch detailed data for filtered coins
    coins_data = fetch_coins_data(all_symbols_data, potential_and_wallet_coins)

    # Save coins data to a file
    save_data_to_file(coins_data, "market", "coins_data")

    return coins_data, wallet_balance

def fetch_all_symbols_data():
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
    # Define filter thresholds
    price_change_threshold = config["PRICE_CHANGE_THRESHOLD"]
    price_range_volatility_threshold = config["PRICE_RANGE_VOLATILITY_THRESHOLD"]

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

def fetch_coins_data(all_symbols_data, potential_and_wallet_coins):
    coins_data = {}

    # Extract data from all_symbols_data
    symbols = all_symbols_data["exchange_info"]["symbols"]
    active_symbols = all_symbols_data["active_symbols"]
    prices = {price["symbol"]: float(price["price"]) for price in all_symbols_data["prices"]}
    stats = {stat["symbol"]: stat for stat in all_symbols_data["stats"] if stat["symbol"] in active_symbols}

    for coin in potential_and_wallet_coins:
        if coin == "USDT":
            continue

        if coin == "BNB":
            continue

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

        # Initialize data collector
        candlestick_data = {}

        # Collect data for each pairing
        for pair in trading_pairs:
            candlestick_data[pair] = client.klines(symbol=pair, interval='1h', limit=24)

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
            "candlesticks": candlestick_data,  # Candlesticks (OHLC data)
        }

    return coins_data