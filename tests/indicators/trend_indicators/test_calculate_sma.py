import pandas as pd
from unittest.mock import patch
from tests.indicators.mock_data import MOCK_CONFIG_VALUES

# Mock `load_config_values`
with patch("utils.file_utils.load_config_values", return_value=MOCK_CONFIG_VALUES):
    from indicators.trend_indicators import calculate_sma

def test_calculate_sma_with_valid_data():
    # Test with a valid list of prices
    prices = [10, 20, 30, 40, 50]
    window = 3
    result = calculate_sma(prices, window=window)
    expected_result = pd.Series(prices).rolling(window=window).mean()
    pd.testing.assert_series_equal(result, expected_result)

def test_calculate_sma_with_empty_prices():
    # Test with an empty list of prices
    prices = []
    window = 14
    result = calculate_sma(prices, window=window)
    assert result is None  # Explicitly check for `None`

def test_calculate_sma_with_window_larger_than_prices_length():
    # Test when the rolling window is larger than the length of prices
    prices = [10, 20]
    window = 5
    result = calculate_sma(prices, window=window)
    expected_result = pd.Series(prices).rolling(window=window).mean()
    pd.testing.assert_series_equal(result, expected_result)

def test_calculate_sma_with_default_window():
    # Test without specifying a window (should default to 14)
    prices = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150]
    result = calculate_sma(prices)
    expected_result = pd.Series(prices).rolling(window=14).mean()
    pd.testing.assert_series_equal(result, expected_result)

def test_calculate_sma_with_window_one():
    # Test with a window size of 1
    prices = [10, 20, 30, 40, 50]
    window = 1
    result = calculate_sma(prices, window=window)
    expected_result = pd.Series(prices)
    pd.testing.assert_series_equal(result, expected_result)

def test_calculate_sma_with_float_prices():
    # Test with floating-point prices
    prices = [10.5, 20.3, 30.7, 40.2, 50.1]
    window = 3
    result = calculate_sma(prices, window=window)
    expected_result = pd.Series(prices).rolling(window=window).mean()
    pd.testing.assert_series_equal(result, expected_result)

def test_calculate_sma_with_negative_window():
    # Test with a negative window value
    prices = [10, 20, 30, 40, 50]
    window = -3
    try:
        calculate_sma(prices, window=window)
        assert False, "Expected an exception for negative window size"
    except ValueError as e:
        assert str(e) == "window must be an integer >= 1"

def test_calculate_sma_with_zero_window():
    # Test with a zero window value
    prices = [10, 20, 30, 40, 50]
    window = 0
    try:
        calculate_sma(prices, window=window)
        assert False, "Expected an exception for zero window size"
    except ValueError as e:
        assert str(e) == "window must be an integer >= 1"
