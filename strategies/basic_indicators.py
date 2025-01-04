import pandas as pd


def calculate_sma(prices, window=14):
    """
    Calculate Simple Moving Average (SMA).

    :param prices: List or array of prices.
    :param window: Number of periods for SMA calculation.
    :return: SMA values as a pandas Series.
    """
    if not prices:
        return None
    prices_series = pd.Series(prices)
    return prices_series.rolling(window=window).mean()


def calculate_ema(prices, window=14):
    """
    Calculate Exponential Moving Average (EMA).

    :param prices: List or array of prices.
    :param window: Number of periods for EMA calculation.
    :return: EMA values as a pandas Series.
    """
    if not prices:
        return None
    prices_series = pd.Series(prices)
    return prices_series.ewm(span=window, adjust=False).mean()


def calculate_rsi(prices, window=14):
    """
    Calculate Relative Strength Index (RSI).

    :param prices: List or array of prices.
    :param window: Number of periods for RSI calculation.
    :return: RSI values as a pandas Series.
    """
    if not prices or len(prices) < window:
        return None
    prices_series = pd.Series(prices)
    delta = prices_series.diff()

    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi
