import pandas as pd

def calculate_bollinger_bands(prices, window=20, num_std_dev=2):
    """
    Calculate Bollinger Bands.

    Parameters:
        prices (list or pd.Series): List or array of prices.
        window (int, optional): Number of periods for SMA (default 20).
        num_std_dev (int, optional): Number of standard deviations (default 2).

    Returns:
        dict: Bollinger Bands with 'middle', 'upper', and 'lower' keys.
    """
    if not prices or len(prices) < window:
        return None
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
    """
    Calculate Average True Range (ATR).

    Parameters:
        highs (list or pd.Series): High prices.
        lows (list or pd.Series): Low prices.
        closes (list or pd.Series): Close prices.
        window (int, optional): Period for ATR calculation (default 14).

    Returns:
        pd.Series: ATR values as a pandas Series.
    """
    if len(highs) < window or len(lows) < window or len(closes) < window:
        return None

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
        indicators['BollingerBands'] = calculate_bollinger_bands(close_prices)

        # Average True Range (ATR)
        atr_period = 14
        indicators['ATR'] = calculate_atr(high_prices, low_prices, close_prices, atr_period)

    except Exception as e:
        print(f"Error in calculating advanced indicators: {e}")

    return indicators