import numpy as np

from indicators.trend_indicators import calculate_trend_indicators, simplify_trend_indicators
from indicators.momentum_indicators import calculate_momentum_indicators, simplify_momentum_indicators
from indicators.volatility_indicators import calculate_volatility_indicators, simplify_volatility_indicators
from utils.file_utils import save_data_to_file

def calculate_indicators(coins_data):
    # Get indicators
    indicators = apply_indicators(coins_data)

    # Clean indicators
    cleaned_indicators = clean_indicators(indicators)

    # Save indicators to a file
    save_data_to_file(cleaned_indicators, "indicators", "indicators")

    # Return the cleaned_indicators
    return cleaned_indicators

def extract_ohlc_prices(coins_data, coin):
    candlestick_data = coins_data[coin].get("candlesticks", {})

    # Lists to store prices
    high_prices = []
    low_prices = []
    close_prices = []

    # Loop through all candlestick data for each pair and extract high, low, and close prices
    for pair, data_list in candlestick_data.items():
        high_prices.extend([float(ohlcv[2]) for ohlcv in data_list])
        low_prices.extend([float(ohlcv[3]) for ohlcv in data_list])
        close_prices.extend([float(ohlcv[4]) for ohlcv in data_list])

    return high_prices, low_prices, close_prices

def clean_indicators(indicators):
    def convert_value(value):
        # Convert NumPy scalars to Python types
        if isinstance(value, (np.float64, np.float32)):
            return round(float(value), 4)
        elif isinstance(value, (np.int64, np.int32, np.int_)):
            return int(value)
        elif isinstance(value, np.bool_):
            return bool(value)
        elif isinstance(value, dict):
            return {k: convert_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [convert_value(v) for v in value]
        elif isinstance(value, float):
            return round(value, 4)
        else:
            return value

    # Clean the entire indicators dictionary
    return {coin: convert_value(data) for coin, data in indicators.items()}

def apply_indicators(coins_data):
    indicators = {}

    # Loop through each coin
    for coin, data in coins_data.items():
        try:
            # Extract high, low, close prices
            high_prices, low_prices, close_prices = extract_ohlc_prices(coins_data, coin)

            # Validate there are enough prices for indicator calculation
            if len(close_prices) < 2:
                print(f"Not enough close prices for {coin}, skipping...")
                continue

            # Calculate indicators
            trend_indicators = calculate_trend_indicators(high_prices, low_prices, close_prices)
            momentum_indicators = calculate_momentum_indicators(high_prices, low_prices, close_prices)
            volatility_indicators = calculate_volatility_indicators(high_prices, low_prices, close_prices)

            # Simplify the data into the latest value or actionable signals
            simplified_trend = simplify_trend_indicators(trend_indicators, close_prices)
            simplified_momentum = simplify_momentum_indicators(momentum_indicators)
            simplified_volatility = simplify_volatility_indicators(volatility_indicators, close_prices)

            # Combine simplified indicators into the final structure
            indicators[coin] = {
                'trend': simplified_trend,
                'momentum': simplified_momentum,
                'volatility': simplified_volatility
            }

        except Exception as e:
            print(f"Error calculating indicators for {coin}: {e}")

    return indicators


