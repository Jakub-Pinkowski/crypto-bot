import pandas as pd
from unittest.mock import patch
from tests.indicators.mock_data import MOCK_CONFIG_VALUES

# Mock `load_config_values`
with patch("utils.file_utils.load_config_values", return_value=MOCK_CONFIG_VALUES):
    from indicators.volatility_indicators import calculate_bollinger_bands


def test_calculate_bollinger_bands_with_valid_data():
    # Test with a valid list of prices
    prices = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    window = 3
    num_std_dev = 2
    result = calculate_bollinger_bands(prices, window=window, num_std_dev=num_std_dev)

    prices_series = pd.Series(prices)
    middle_band = prices_series.rolling(window=window).mean()
    std_dev = prices_series.rolling(window=window).std()
    upper_band = middle_band + (std_dev * num_std_dev)
    lower_band = middle_band - (std_dev * num_std_dev)

    expected_result = {
        'middle_band': middle_band,
        'upper_band': upper_band,
        'lower_band': lower_band
    }

    pd.testing.assert_series_equal(result['middle_band'], expected_result['middle_band'])
    pd.testing.assert_series_equal(result['upper_band'], expected_result['upper_band'])
    pd.testing.assert_series_equal(result['lower_band'], expected_result['lower_band'])


def test_calculate_bollinger_bands_with_empty_prices():
    # Test with an empty list of prices
    prices = []
    window = 14
    num_std_dev = 2
    result = calculate_bollinger_bands(prices, window=window, num_std_dev=num_std_dev)
    assert result is None  # Explicitly check for `None`


def test_calculate_bollinger_bands_with_window_larger_than_prices_length():
    # Test when the rolling window is larger than the length of prices
    prices = [10, 20]
    window = 5
    num_std_dev = 2
    result = calculate_bollinger_bands(prices, window=window, num_std_dev=num_std_dev)
    assert result is None  # Result should be None as window size is larger than the price list


def test_calculate_bollinger_bands_with_default_window():
    # Test without specifying a window (should default to 20)
    prices = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200]
    num_std_dev = 2
    result = calculate_bollinger_bands(prices, num_std_dev=num_std_dev)

    # Create expected result using a window of 20
    prices_series = pd.Series(prices)
    middle_band = prices_series.rolling(window=20).mean()
    std_dev = prices_series.rolling(window=20).std()
    upper_band = middle_band + (std_dev * num_std_dev)
    lower_band = middle_band - (std_dev * num_std_dev)

    # Expected dictionary with the calculated bands
    expected_result = {
        'middle_band': middle_band,
        'upper_band': upper_band,
        'lower_band': lower_band
    }

    # Validate that the result matches the expected values
    pd.testing.assert_series_equal(result['middle_band'], expected_result['middle_band'])
    pd.testing.assert_series_equal(result['upper_band'], expected_result['upper_band'])
    pd.testing.assert_series_equal(result['lower_band'], expected_result['lower_band'])


def test_calculate_bollinger_bands_with_window_one():
    # Test with a window size of 1
    prices = [10, 20, 30, 40, 50]
    window = 1
    num_std_dev = 2
    result = calculate_bollinger_bands(prices, window=window, num_std_dev=num_std_dev)

    prices_series = pd.Series(prices)
    middle_band = prices_series.rolling(window=window).mean()
    std_dev = prices_series.rolling(window=window).std()
    upper_band = middle_band + (std_dev * num_std_dev)
    lower_band = middle_band - (std_dev * num_std_dev)

    expected_result = {
        'middle_band': middle_band,
        'upper_band': upper_band,
        'lower_band': lower_band
    }

    pd.testing.assert_series_equal(result['middle_band'], expected_result['middle_band'])
    pd.testing.assert_series_equal(result['upper_band'], expected_result['upper_band'])
    pd.testing.assert_series_equal(result['lower_band'], expected_result['lower_band'])


def test_calculate_bollinger_bands_with_float_prices():
    # Test with floating-point prices
    prices = [10.5, 20.3, 30.7, 40.2, 50.1]
    window = 3
    num_std_dev = 2
    result = calculate_bollinger_bands(prices, window=window, num_std_dev=num_std_dev)

    prices_series = pd.Series(prices)
    middle_band = prices_series.rolling(window=window).mean()
    std_dev = prices_series.rolling(window=window).std()
    upper_band = middle_band + (std_dev * num_std_dev)
    lower_band = middle_band - (std_dev * num_std_dev)

    expected_result = {
        'middle_band': middle_band,
        'upper_band': upper_band,
        'lower_band': lower_band
    }

    pd.testing.assert_series_equal(result['middle_band'], expected_result['middle_band'])
    pd.testing.assert_series_equal(result['upper_band'], expected_result['upper_band'])
    pd.testing.assert_series_equal(result['lower_band'], expected_result['lower_band'])


def test_calculate_bollinger_bands_with_negative_window():
    # Test with a negative window value
    prices = [10, 20, 30, 40, 50]
    window = -3
    num_std_dev = 2
    try:
        calculate_bollinger_bands(prices, window=window, num_std_dev=num_std_dev)
        assert False, "Expected an exception for negative window size"
    except ValueError as e:
        assert str(e) == "window must be an integer >= 1"


def test_calculate_bollinger_bands_with_zero_window():
    # Test with a zero window value
    prices = [10, 20, 30, 40, 50]
    window = 0
    num_std_dev = 2
    try:
        calculate_bollinger_bands(prices, window=window, num_std_dev=num_std_dev)
        assert False, "Expected an exception for zero window size"
    except ValueError as e:
        assert str(e) == "window must be an integer >= 1"