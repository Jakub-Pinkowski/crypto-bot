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

def calculate_stochastic_oscillator(highs, lows, closes, window=14, smooth_window=3):
    """
    Calculate Stochastic Oscillator (%K and %D).

    Parameters:
        highs (list or pd.Series): High prices.
        lows (list or pd.Series): Low prices.
        closes (list or pd.Series): Close prices.
        window (int, optional): Period for %K calculation (default 14).
        smooth_window (int, optional): Period for smoothing %D (default 3).

    Returns:
        dict: {'%K': %K values, '%D': %D values}.
    """
    if len(highs) < window or len(lows) < window or len(closes) < window:
        return None

    highest_high = pd.Series(highs).rolling(window=window).max()
    lowest_low = pd.Series(lows).rolling(window=window).min()
    percent_k = ((pd.Series(closes) - lowest_low) / (highest_high - lowest_low)) * 100
    percent_d = percent_k.rolling(window=smooth_window).mean()  # Smoothed %K

    return {
        '%K': percent_k,
        '%D': percent_d
    }

def calculate_williams_r(highs, lows, closes, window=14):
    """
    Calculate Williams %R.

    Parameters:
        highs (list or pd.Series): High prices.
        lows (list or pd.Series): Low prices.
        closes (list or pd.Series): Close prices.
        window (int, optional): Period for %R calculation (default 14).

    Returns:
        pd.Series: Williams %R values as a pandas Series.
    """
    if len(highs) < window or len(lows) < window or len(closes) < window:
        return None

    highest_high = pd.Series(highs).rolling(window=window).max()
    lowest_low = pd.Series(lows).rolling(window=window).min()
    williams_r = ((highest_high - pd.Series(closes)) / (highest_high - lowest_low)) * -100

    return williams_r

def calculate_cci(highs, lows, closes, window=20):
    """
    Calculate Commodity Channel Index (CCI).

    Parameters:
        highs (list or pd.Series): High prices.
        lows (list or pd.Series): Low prices.
        closes (list or pd.Series): Close prices.
        window (int, optional): Period for CCI calculation (default 20).

    Returns:
        pd.Series: CCI values as a pandas Series.
    """
    if len(highs) < window or len(lows) < window or len(closes) < window:
        return None

    # Calculate Typical Price (TP) = (High + Low + Close) / 3
    typical_price = (pd.Series(highs) + pd.Series(lows) + pd.Series(closes)) / 3

    # Calculate SMA of Typical Price
    tp_sma = typical_price.rolling(window=window).mean()

    # Calculate Mean Deviation (manually)
    mean_deviation = typical_price.rolling(window=window).apply(
        lambda x: pd.Series(x).sub(x.mean()).abs().mean(), raw=False
    )

    # Calculate CCI
    cci = (typical_price - tp_sma) / (0.015 * mean_deviation)

    return cci
