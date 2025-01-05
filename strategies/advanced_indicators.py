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


def calculate_macd(prices, short_window=12, long_window=26, signal_window=9):
    """
    Calculate MACD (Moving Average Convergence Divergence).

    Parameters:
        prices (list or pd.Series): List or array of prices.
        short_window (int, optional): Period for short EMA (default 12).
        long_window (int, optional): Period for long EMA (default 26).
        signal_window (int, optional): Period for Signal Line EMA (default 9).

    Returns:
        dict: MACD components - 'macd_line', 'signal_line', 'histogram'.
    """
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

