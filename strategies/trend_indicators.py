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

def calculate_ichimoku_cloud(highs, lows, closes, tenkan_window=9, kijun_window=26, senkou_b_window=52,
                             senkou_shift=26):
    """
    Calculate Ichimoku Cloud components.

    Parameters:
        highs (list or pd.Series): High prices.
        lows (list or pd.Series): Low prices.
        closes (list or pd.Series): Closing prices.
        tenkan_window (int, optional): Period for Tenkan-sen (default 9).
        kijun_window (int, optional): Period for Kijun-sen (default 26).
        senkou_b_window (int, optional): Period for Senkou Span B (default 52).
        senkou_shift (int, optional): Forward shift for Senkou Spans (default 26).

    Returns:
        dict: Ichimoku Cloud components - 'tenkan_sen', 'kijun_sen', 'senkou_span_a',
              'senkou_span_b', 'chikou_span'.
    """
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
