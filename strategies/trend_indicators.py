import pandas as pd

def calculate_sma(prices, window=14):
    """
    Calculate Simple Moving Average (SMA).

    Detailed explanation including key steps or concepts:
    - Calculate a rolling window mean on the prices.
    - Use pandas' rolling method to handle the computation.

    Parameters:
        prices (list or pd.Series): List or array of prices.
        window (int, optional): Number of periods for SMA calculation (default 14).

    Returns:
        pd.Series: SMA values as a pandas Series.
    """
    if not prices:
        return None
    prices_series = pd.Series(prices)
    return prices_series.rolling(window=window).mean()


def calculate_ema(prices, window=14):
    """
    Calculate Exponential Moving Average (EMA).

    Detailed explanation including key steps or concepts:
    - Use pandas' ewm method to compute the EMA.
    - EWM method applies weighted averages to prices, with recent prices weighted higher.

    Parameters:
        prices (list or pd.Series): List or array of prices.
        window (int, optional): Number of periods for EMA calculation (default 14).

    Returns:
        pd.Series: EMA values as a pandas Series.
    """
    if not prices:
        return None
    prices_series = pd.Series(prices)
    return prices_series.ewm(span=window, adjust=False).mean()

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


