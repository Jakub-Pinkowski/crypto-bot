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


def calculate_rsi(prices, window=14):
    """
    Calculate Relative Strength Index (RSI).

    Detailed explanation including key steps or concepts:
    - Compute the price differences and separate into gains and losses.
    - Calculate the average gain and loss over a rolling window.
    - Compute the Relative Strength (RS) and use it to calculate RSI.

    Parameters:
        prices (list or pd.Series): List or array of prices.
        window (int, optional): Number of periods for RSI calculation (default 14).

    Returns:
        pd.Series: RSI values as a pandas Series.
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
