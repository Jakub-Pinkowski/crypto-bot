def scoring_system_1(rsi, sma_score, macd_histogram):
    """
    RSI + SMA + MACD (Default). Standard scoring using all three indicators.
    """
    return rsi * 1.5 + sma_score * -2 + macd_histogram * 3


def scoring_system_2(rsi, sma_score, macd_histogram):
    """
    RSI + SMA only (When MACD data is unavailable).
    """
    return rsi * 2 + sma_score * -3  # Adjusted weights to compensate for missing MACD


def scoring_system_3(rsi, sma_score, macd_histogram):
    """
    SMA-focused scoring with light RSI impact (for trend-following strategies).
    """
    return sma_score * -4 + rsi * 1  # Heavier weight for SMA signaling