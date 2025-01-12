import pandas as pd
from utils.file_utils import load_config_values

config = load_config_values("TREND_INDICATORS")

def calculate_sma(prices, window=14):
    if not prices:
        return None

    # Validate the window parameter
    if not isinstance(window, int) or window < 1:
        raise ValueError("window must be an integer >= 1")


    prices_series = pd.Series(prices)
    return prices_series.rolling(window=window).mean()

def calculate_ema(prices, window=14):
    if not prices:
        return None

    # Validate the window parameter
    if not isinstance(window, int) or window < 1:
        raise ValueError("window must be >= 1")

    prices_series = pd.Series(prices)
    return prices_series.ewm(span=window, adjust=False).mean()

def calculate_macd(prices, short_window=12, long_window=26, signal_window=9):
    if not prices or len(prices) < long_window:
        return None
    prices_series = pd.Series(prices)
    short_ema = prices_series.ewm(span=short_window, adjust=False).mean()
    long_ema = prices_series.ewm(span=long_window, adjust=False).mean()
    macd_line = short_ema - long_ema
    signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()
    histogram = macd_line - signal_line
    return {
        'macd_line': macd_line,
        'signal_line': signal_line,
        'histogram': histogram
    }

def calculate_ichimoku_cloud(highs, lows, closes, tenkan_window=9, kijun_window=26, senkou_b_window=52, senkou_shift=26):
    if len(highs) < max(tenkan_window, kijun_window, senkou_b_window):
        return None

    highs_series = pd.Series(highs)
    lows_series = pd.Series(lows)
    closes_series = pd.Series(closes)

    # Calculate Tenkan-sen (Conversion Line)
    tenkan_sen = (highs_series.rolling(window=tenkan_window).max() +
                  lows_series.rolling(window=tenkan_window).min()) / 2

    # Calculate Kijun-sen (Base Line)
    kijun_sen = (highs_series.rolling(window=kijun_window).max() +
                 lows_series.rolling(window=kijun_window).min()) / 2

    # Calculate Senkou Span A (Leading Span A)
    senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(senkou_shift)

    # Calculate Senkou Span B (Leading Span B)
    senkou_span_b = ((highs_series.rolling(window=senkou_b_window).max() +
                      lows_series.rolling(window=senkou_b_window).min()) / 2).shift(senkou_shift)

    # Calculate Chikou Span (Lagging Span)
    chikou_span = closes_series.shift(-senkou_shift)

    return {
        'tenkan_sen': tenkan_sen,
        'kijun_sen': kijun_sen,
        'senkou_span_a': senkou_span_a,
        'senkou_span_b': senkou_span_b,
        'chikou_span': chikou_span
    }

def calculate_trend_indicators(high_prices, low_prices, close_prices):
    indicators = {}
    try:
        # Simple Moving Average (SMA)
        sma_period = config['TREND_INDICATORS']['SMA_WINDOW']
        indicators['SMA'] = calculate_sma(close_prices, sma_period)

        # Exponential Moving Average (EMA)
        ema_period = config['TREND_INDICATORS']['EMA_WINDOW']
        indicators['EMA'] = calculate_ema(close_prices, ema_period)

        # MACD
        macd_config = config['TREND_INDICATORS']['MACD']  # Extract MACD configuration
        macd_short_window = macd_config['SHORT_WINDOW']
        macd_long_window = macd_config['LONG_WINDOW']
        macd_signal_window = macd_config['SIGNAL_WINDOW']
        indicators['MACD'] = calculate_macd(close_prices, macd_short_window, macd_long_window, macd_signal_window)

        # Calculate Ichimoku Cloud
        ichimoku_config = config['TREND_INDICATORS']['ICHIMOKU']  # Extract Ichimoku configuration
        tenkan_window = ichimoku_config['TENKAN_WINDOW']
        kijun_window = ichimoku_config['KIJUN_WINDOW']
        senkou_b_window = ichimoku_config['SENKOU_B_WINDOW']
        senkou_shift = ichimoku_config['SENKOU_SHIFT']
        indicators['Ichimoku'] = calculate_ichimoku_cloud(high_prices, low_prices, close_prices, tenkan_window, kijun_window, senkou_b_window, senkou_shift)

    except Exception as e:
        print(f"Error in calculating basic indicators: {e}")

    return indicators

def simplify_trend_indicators(trend_indicators, close_prices):
    simplified = {}

    # Extract the latest value for each trend indicator
    if "SMA" in trend_indicators:
        simplified["SMA"] = trend_indicators["SMA"].iloc[-1]  # Latest SMA value

        # Check if close price is above or below the SMA
        simplified["above_SMA"] = close_prices[-1] > simplified["SMA"]

    if "EMA" in trend_indicators:
        simplified["EMA"] = trend_indicators["EMA"].iloc[-1]  # Latest EMA value

    # MACD: Add signal direction (e.g., bullish or bearish crossover)
    if "MACD" in trend_indicators and trend_indicators["MACD"]:
        macd_data = trend_indicators["MACD"]

        # Safely extract MACD components
        simplified["MACD_current"] = macd_data["macd_line"].iloc[-1] if "macd_line" in macd_data else None
        simplified["MACD_signal"] = macd_data["signal_line"].iloc[-1] if "signal_line" in macd_data else None
        simplified["MACD_histogram"] = macd_data["histogram"].iloc[-1] if "histogram" in macd_data else None

        # Determine the trend based on MACD and Signal line values
        if simplified["MACD_current"] and simplified["MACD_signal"]:
            simplified["MACD_trend"] = (
                "bullish" if simplified["MACD_current"] > simplified["MACD_signal"] else "bearish"
            )

    return simplified