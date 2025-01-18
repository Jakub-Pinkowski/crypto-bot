from unittest.mock import patch

import pandas as pd

from tests.indicators.mock_data import MOCK_CONFIG_VALUES

# Mock `load_config_values`
with patch("utils.file_utils.load_config_values", return_value=MOCK_CONFIG_VALUES):
    from indicators.momentum_indicators import calculate_williams_r


def test_calculate_williams_r_with_valid_data():
    # Test with a valid list of highs, lows, and closes
    highs = [44, 46, 47, 45, 43, 42, 44, 45]
    lows = [40, 42, 43, 41, 39, 38, 40, 41]
    closes = [43, 45, 46, 44, 42, 43, 45, 46]
    window = 3
    result = calculate_williams_r(highs, lows, closes, window=window)

    # Calculate expected Williams %R
    highest_high = pd.Series(highs).rolling(window=window).max()
    lowest_low = pd.Series(lows).rolling(window=window).min()
    expected_williams_r = ((highest_high - pd.Series(closes)) / (highest_high - lowest_low)) * -100

    # Ensure both result and expected_williams_r are the same length
    assert len(result) == len(expected_williams_r)

    # Check if the values are equal, but ignore NaNs at the start
    pd.testing.assert_series_equal(result, expected_williams_r, check_like=True)


def test_calculate_williams_r_with_window_less_than_two():
    # Test with a window size of 1, should raise an exception
    highs = [44, 46, 47, 45, 43, 42, 44, 45]
    lows = [40, 42, 43, 41, 39, 38, 40, 41]
    closes = [43, 45, 46, 44, 42, 43, 45, 46]
    window = 1
    try:
        calculate_williams_r(highs, lows, closes, window=window)
        assert False, "Expected an exception for window size of 1"
    except ValueError as e:
        assert str(e) == "window must be an integer >= 2"


def test_calculate_williams_r_with_empty_data():
    # Test with an empty list of highs, lows, and closes
    highs = []
    lows = []
    closes = []
    window = 14
    result = calculate_williams_r(highs, lows, closes, window=window)
    assert result is None  # Expect None because the data is empty


def test_calculate_williams_r_with_window_larger_than_data_length():
    # Test when the window is larger than the length of highs, lows, or closes
    highs = [44, 46]
    lows = [40, 42]
    closes = [43, 45]
    window = 5
    result = calculate_williams_r(highs, lows, closes, window=window)
    assert result is None  # Expect None because window is larger than data length


def test_calculate_williams_r_with_valid_data_large_window():
    # Test with a valid list of highs, lows, and closes, and a larger window size
    highs = [44, 46, 47, 45, 43, 42, 44, 45, 46, 47, 48, 49, 50, 51]
    lows = [40, 42, 43, 41, 39, 38, 40, 41, 42, 43, 44, 45, 46, 47]
    closes = [43, 45, 46, 44, 42, 43, 45, 46, 47, 48, 47, 46, 45, 44]
    window = 7
    result = calculate_williams_r(highs, lows, closes, window=window)

    # Calculate expected Williams %R
    highest_high = pd.Series(highs).rolling(window=window).max()
    lowest_low = pd.Series(lows).rolling(window=window).min()
    expected_williams_r = ((highest_high - pd.Series(closes)) / (highest_high - lowest_low)) * -100

    # Ensure both result and expected_williams_r are the same length
    assert len(result) == len(expected_williams_r)

    # Check if the values are equal, but ignore NaNs at the start
    pd.testing.assert_series_equal(result, expected_williams_r, check_like=True)
