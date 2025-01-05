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