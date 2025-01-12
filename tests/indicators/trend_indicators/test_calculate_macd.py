import pandas as pd
from unittest.mock import patch
from tests.indicators.mock_data import MOCK_CONFIG_VALUES

# Mock `load_config_values`
with patch("utils.file_utils.load_config_values", return_value=MOCK_CONFIG_VALUES):
    from indicators.trend_indicators import calculate_macd


def test_calculate_macd_with_valid_data():
    # Test with a valid list of prices
    prices = [i for i in range(1, 50)]
    short_window = 12
    long_window = 26
    signal_window = 9
    result = calculate_macd(prices, short_window, long_window, signal_window)

    prices_series = pd.Series(prices)
    short_ema = prices_series.ewm(span=short_window, adjust=False).mean()
    long_ema = prices_series.ewm(span=long_window, adjust=False).mean()
    macd_line = short_ema - long_ema
    signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()
    histogram = macd_line - signal_line

    # Validate the returned components
    pd.testing.assert_series_equal(result['macd_line'], macd_line)
    pd.testing.assert_series_equal(result['signal_line'], signal_line)
    pd.testing.assert_series_equal(result['histogram'], histogram)


def test_calculate_macd_with_empty_prices():
    # Test with an empty list of prices
    prices = []
    result = calculate_macd(prices)
    assert result is None


def test_calculate_macd_with_insufficient_prices():
    # Test when the list of prices is smaller than the long_window
    prices = [10, 20, 30]  # Length < long_window
    short_window = 12
    long_window = 26
    result = calculate_macd(prices, short_window, long_window)
    assert result is None


def test_calculate_macd_with_custom_windows():
    # Test with custom short, long, and signal windows
    prices = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150]
    short_window = 5
    long_window = 10
    signal_window = 3
    result = calculate_macd(prices, short_window, long_window, signal_window)

    prices_series = pd.Series(prices)
    short_ema = prices_series.ewm(span=short_window, adjust=False).mean()
    long_ema = prices_series.ewm(span=long_window, adjust=False).mean()
    macd_line = short_ema - long_ema
    signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()
    histogram = macd_line - signal_line

    # Validate the returned components
    pd.testing.assert_series_equal(result['macd_line'], macd_line)
    pd.testing.assert_series_equal(result['signal_line'], signal_line)
    pd.testing.assert_series_equal(result['histogram'], histogram)


def test_calculate_macd_with_float_prices():
    # Test with floating-point prices
    prices = [10.5, 20.3, 30.7, 40.2, 50.1, 60.8, 70.4, 80.9, 90.2, 100.5,
              110.3, 120.7, 130.4, 140.8, 150.2, 160.5, 170.8, 180.3, 190.7,
              200.5, 210.9, 220.3, 230.7, 240.1, 250.6, 260.8]
    result = calculate_macd(prices)

    prices_series = pd.Series(prices)
    short_ema = prices_series.ewm(span=12, adjust=False).mean()
    long_ema = prices_series.ewm(span=26, adjust=False).mean()
    macd_line = short_ema - long_ema
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    histogram = macd_line - signal_line

    # Validate the returned components
    pd.testing.assert_series_equal(result['macd_line'], macd_line)
    pd.testing.assert_series_equal(result['signal_line'], signal_line)
    pd.testing.assert_series_equal(result['histogram'], histogram)


def test_calculate_macd_with_negative_prices():
    # Test with negative prices
    prices = [-i for i in range(1, 50)]
    result = calculate_macd(prices)

    prices_series = pd.Series(prices)
    short_ema = prices_series.ewm(span=12, adjust=False).mean()
    long_ema = prices_series.ewm(span=26, adjust=False).mean()
    macd_line = short_ema - long_ema
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    histogram = macd_line - signal_line

    # Validate the returned components
    pd.testing.assert_series_equal(result['macd_line'], macd_line)
    pd.testing.assert_series_equal(result['signal_line'], signal_line)
    pd.testing.assert_series_equal(result['histogram'], histogram)


def test_calculate_macd_with_single_price():
    # Test with a single price
    prices = [100]
    result = calculate_macd(prices)
    assert result is None  # MACD cannot be calculated with only one price