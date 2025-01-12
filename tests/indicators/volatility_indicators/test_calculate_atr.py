import pandas as pd
from unittest.mock import patch
from tests.indicators.mock_data import MOCK_CONFIG_VALUES

# Mock `load_config_values`
with patch("utils.file_utils.load_config_values", return_value=MOCK_CONFIG_VALUES):
    from indicators.volatility_indicators import calculate_atr

def test_calculate_atr_with_valid_data():
    # Test with valid data
    highs = [20, 22, 24, 26, 28, 30]
    lows = [10, 11, 12, 13, 14, 15]
    closes = [15, 16, 17, 18, 19, 20]
    window = 3
    result = calculate_atr(highs, lows, closes, window=window)

    # Calculate expected ATR using a rolling window of 3
    highs_series = pd.Series(highs)
    lows_series = pd.Series(lows)
    closes_series = pd.Series(closes)
    true_range = pd.concat([
        highs_series - lows_series,
        (highs_series - closes_series.shift(1)).abs(),
        (lows_series - closes_series.shift(1)).abs()
    ], axis=1).max(axis=1)

    expected_result = true_range.rolling(window=window).mean()

    # Validate that the result matches the expected values
    pd.testing.assert_series_equal(result, expected_result)

def test_calculate_atr_with_empty_lists():
    # Test with empty lists
    highs = []
    lows = []
    closes = []
    window = 14
    result = calculate_atr(highs, lows, closes, window=window)
    assert result is None  # Explicitly check for `None`

def test_calculate_atr_with_insufficient_data():
    # Test when the length of inputs is less than the window size
    highs = [20, 22, 24]
    lows = [10, 12, 14]
    closes = [15, 16, 17]
    window = 5
    result = calculate_atr(highs, lows, closes, window=window)
    assert result is None  # The function should return `None` due to insufficient data

def test_calculate_atr_with_default_window():
    # Test with default window size (14)
    highs = [20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50]
    lows = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
    closes = [15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]
    result = calculate_atr(highs, lows, closes)

    # Calculate expected ATR using a rolling window of 14
    highs_series = pd.Series(highs)
    lows_series = pd.Series(lows)
    closes_series = pd.Series(closes)
    true_range = pd.concat([
        highs_series - lows_series,
        (highs_series - closes_series.shift(1)).abs(),
        (lows_series - closes_series.shift(1)).abs()
    ], axis=1).max(axis=1)

    expected_result = true_range.rolling(window=14).mean()

    # Validate that the result matches the expected values
    pd.testing.assert_series_equal(result, expected_result)

def test_calculate_atr_with_window_of_one():
    # Test with a window size of 1
    highs = [20, 22, 24, 26, 28, 30]
    lows = [10, 11, 12, 13, 14, 15]
    closes = [15, 16, 17, 18, 19, 20]
    window = 1
    result = calculate_atr(highs, lows, closes, window=window)

    # Calculate expected ATR using a rolling window of 1
    highs_series = pd.Series(highs)
    lows_series = pd.Series(lows)
    closes_series = pd.Series(closes)
    true_range = pd.concat([
        highs_series - lows_series,
        (highs_series - closes_series.shift(1)).abs(),
        (lows_series - closes_series.shift(1)).abs()
    ], axis=1).max(axis=1)

    expected_result = true_range.rolling(window=1).mean()

    # Validate that the result matches the expected values
    pd.testing.assert_series_equal(result, expected_result)

def test_calculate_atr_with_negative_window():
    # Test with a negative window value
    highs = [20, 22, 24, 26, 28, 30]
    lows = [10, 11, 12, 13, 14, 15]
    closes = [15, 16, 17, 18, 19, 20]
    window = -3
    try:
        calculate_atr(highs, lows, closes, window=window)
        assert False, "Expected an exception for negative window size"
    except ValueError as e:
        assert str(e) == "window must be an integer >= 1"

def test_calculate_atr_with_zero_window():
    # Test with a zero window value
    highs = [20, 22, 24, 26, 28, 30]
    lows = [10, 11, 12, 13, 14, 15]
    closes = [15, 16, 17, 18, 19, 20]
    window = 0
    try:
        calculate_atr(highs, lows, closes, window=window)
        assert False, "Expected an exception for zero window size"
    except ValueError as e:
        assert str(e) == "window must be an integer >= 1"