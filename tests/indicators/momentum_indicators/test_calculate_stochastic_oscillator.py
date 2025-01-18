from unittest.mock import patch

import pandas as pd

from tests.indicators.mock_data import MOCK_CONFIG_VALUES

# Mock `load_config_values`
with patch("utils.file_utils.load_config_values", return_value=MOCK_CONFIG_VALUES):
    from indicators.momentum_indicators import calculate_stochastic_oscillator


def test_calculate_stochastic_oscillator_with_valid_data():
    # Test with valid lists of highs, lows, and closes
    highs = [44, 46, 47, 45, 43, 42, 44, 45, 46, 47, 45, 44, 46, 47]
    lows = [40, 42, 43, 41, 39, 38, 40, 41, 42, 43, 41, 40, 42, 43]
    closes = [43, 45, 46, 44, 42, 43, 45, 46, 47, 45, 44, 43, 45, 46]
    window = 14
    smooth_window = 3
    result = calculate_stochastic_oscillator(highs, lows, closes, window=window, smooth_window=smooth_window)

    # Calculate expected %K and %D
    highest_high = pd.Series(highs).rolling(window=window).max()
    lowest_low = pd.Series(lows).rolling(window=window).min()
    expected_percent_k = ((pd.Series(closes) - lowest_low) / (highest_high - lowest_low)) * 100
    expected_percent_d = expected_percent_k.rolling(window=smooth_window).mean()

    # Ensure that the results are equal
    pd.testing.assert_series_equal(result['%K'], expected_percent_k, check_like=True)
    pd.testing.assert_series_equal(result['%D'], expected_percent_d, check_like=True)


def test_calculate_stochastic_oscillator_with_short_data():
    # Test with not enough data for the specified window
    highs = [44, 46, 47, 45]
    lows = [40, 42, 43, 41]
    closes = [43, 45, 46, 44]
    window = 14
    smooth_window = 3
    result = calculate_stochastic_oscillator(highs, lows, closes, window=window, smooth_window=smooth_window)
    assert result is None  # Not enough data for window size


def test_calculate_stochastic_oscillator_with_default_smooth_window():
    # Test without specifying a smooth_window (should default to 3)
    highs = [44, 46, 47, 45, 43, 42, 44, 45, 46, 47, 45, 44, 46, 47]
    lows = [40, 42, 43, 41, 39, 38, 40, 41, 42, 43, 41, 40, 42, 43]
    closes = [43, 45, 46, 44, 42, 43, 45, 46, 47, 45, 44, 43, 45, 46]
    result = calculate_stochastic_oscillator(highs, lows, closes)

    # Calculate expected %K and %D with default smooth window of 3
    window = 14
    smooth_window = 3
    highest_high = pd.Series(highs).rolling(window=window).max()
    lowest_low = pd.Series(lows).rolling(window=window).min()
    expected_percent_k = ((pd.Series(closes) - lowest_low) / (highest_high - lowest_low)) * 100
    expected_percent_d = expected_percent_k.rolling(window=smooth_window).mean()

    # Ensure that the results are equal
    pd.testing.assert_series_equal(result['%K'], expected_percent_k, check_like=True)
    pd.testing.assert_series_equal(result['%D'], expected_percent_d, check_like=True)


def test_calculate_stochastic_oscillator_with_window_one():
    # Test with a window size of 1
    highs = [44, 46, 47, 45, 43, 42, 44, 45]
    lows = [40, 42, 43, 41, 39, 38, 40, 41]
    closes = [43, 45, 46, 44, 42, 43, 45, 46]
    window = 1
    try:
        result = calculate_stochastic_oscillator(highs, lows, closes, window=window)
        assert False, "Expected an exception for window size of 1"
    except ValueError as e:
        assert str(e) == "window must be an integer >= 2"


def test_calculate_stochastic_oscillator_with_invalid_window():
    # Test with an invalid window (less than 1)
    highs = [44, 46, 47, 45, 43, 42, 44, 45]
    lows = [40, 42, 43, 41, 39, 38, 40, 41]
    closes = [43, 45, 46, 44, 42, 43, 45, 46]
    window = -3
    smooth_window = 3
    try:
        calculate_stochastic_oscillator(highs, lows, closes, window=window, smooth_window=smooth_window)
        assert False, "Expected an exception for invalid window size"
    except ValueError as e:
        assert str(e) == "window must be an integer >= 2"


def test_calculate_stochastic_oscillator_with_empty_data():
    # Test with empty data
    highs = []
    lows = []
    closes = []
    window = 14
    smooth_window = 3
    result = calculate_stochastic_oscillator(highs, lows, closes, window=window, smooth_window=smooth_window)
    assert result is None  # Cannot calculate with empty data
