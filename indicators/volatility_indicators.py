import pandas as pd

from utils.file_utils import load_config_values

config = load_config_values("VOLATILITY_INDICATORS")

def calculate_bollinger_bands(prices, window=20, num_std_dev=2):
    if not prices or len(prices) < window:
        return None

    # Validate the window parameter
    if not isinstance(window, int) or window < 1:
        raise ValueError("window must be an integer >= 1")

    prices_series = pd.Series(prices)
    middle_band = prices_series.rolling(window=window).mean()
    std_dev = prices_series.rolling(window=window).std()
    upper_band = middle_band + (std_dev * num_std_dev)
    lower_band = middle_band - (std_dev * num_std_dev)
    return {
        'middle_band': middle_band,
        'upper_band': upper_band,
        'lower_band': lower_band
    }

def calculate_atr(highs, lows, closes, window=14):
    if len(highs) < window or len(lows) < window or len(closes) < window:
        return None

    # Validate the window parameter
    if not isinstance(window, int) or window < 1:
        raise ValueError("window must be an integer >= 1")

    highs_series = pd.Series(highs)
    lows_series = pd.Series(lows)
    closes_series = pd.Series(closes)

    # Calculate True Range (TR)
    true_range = pd.concat([
        highs_series - lows_series,
        (highs_series - closes_series.shift(1)).abs(),
        (lows_series - closes_series.shift(1)).abs()
    ], axis=1).max(axis=1)

    # Calculate Average True Range (ATR)
    atr = true_range.rolling(window=window).mean()

    return atr

def calculate_volatility_indicators(high_prices, low_prices, close_prices):
    indicators = {}
    try:
        # Bollinger Bands
        bollinger_config = config['VOLATILITY_INDICATORS']['BOLLINGER_BANDS']
        bollinger_window = bollinger_config['WINDOW']
        num_std_dev = bollinger_config['NUM_STD_DEV']
        indicators['BollingerBands'] = calculate_bollinger_bands(close_prices, bollinger_window, num_std_dev)

        # Average True Range (ATR)
        atr_window = config['VOLATILITY_INDICATORS']['ATR_WINDOW']
        indicators['ATR'] = calculate_atr(high_prices, low_prices, close_prices, atr_window)

    except Exception as e:
        print(f"Error in calculating volatility indicators: {e}")

    return indicators


def simplify_volatility_indicators(volatility_indicators, close_prices):
    simplified = {}

    # Bollinger Bands: Extract the width or position relative to the bands
    if "BollingerBands" in volatility_indicators:
        bands = volatility_indicators["BollingerBands"]

        if "upper_band" in bands and "lower_band" in bands and "middle_band" in bands:
            # Calculate the Bollinger Band width
            simplified["Bollinger_width"] = bands["upper_band"].iloc[-1] - bands["lower_band"].iloc[-1]

            # Check if the close price is above or below the bands
            last_close = close_prices[-1]
            simplified["close_above_upper"] = last_close > bands["upper_band"].iloc[-1]
            simplified["close_below_lower"] = last_close < bands["lower_band"].iloc[-1]

    # ATR (Average True Range): Include volatility signal
    if "ATR" in volatility_indicators:
        simplified["ATR"] = volatility_indicators["ATR"].iloc[-1]

    return simplified