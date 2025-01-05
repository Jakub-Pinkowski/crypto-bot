import pandas as pd

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

