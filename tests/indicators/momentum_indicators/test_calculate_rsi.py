import pandas as pd
from unittest.mock import patch
from tests.indicators.mock_data import MOCK_CONFIG_VALUES

# Mock `load_config_values`
with patch("utils.file_utils.load_config_values", return_value=MOCK_CONFIG_VALUES):
    from indicators.momentum_indicators import calculate_rsi


def test_calculate_rsi_with_valid_data():
    # Test with a valid list of prices
    prices = [44, 46, 47, 45, 43, 42, 44, 45, 46, 47, 45, 44, 46, 47]
    window = 14
    result = calculate_rsi(prices, window=window)

    # Calculate expected RSI
    delta = pd.Series(prices).diff()
    gain = delta.where(delta > 0, 0).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    expected_rsi = 100 - (100 / (1 + rs))

    # Ensure both result and expected_rsi are the same length
    assert len(result) == len(expected_rsi)

    # Check if the values are equal, but ignore NaNs at the start
    pd.testing.assert_series_equal(result, expected_rsi, check_like=True)

# Test with an empty list of prices
def test_calculate_rsi_with_empty_prices():
    prices = []
    window = 14
    result = calculate_rsi(prices, window=window)
    assert result is None

# Test with a window size larger than the length of prices
def test_calculate_rsi_with_window_larger_than_prices_length():
    prices = [44, 46, 47]
    window = 5
    result = calculate_rsi(prices, window=window)
    assert result is None  # Should return None because window size is larger than price data

# Test with the default window size (14)
def test_calculate_rsi_with_default_window():
    prices = [44, 46, 47, 45, 43, 42, 44, 45, 46, 47, 45, 44, 46, 47, 48]
    result = calculate_rsi(prices)  # Default window size of 14
    assert result is not None  # Check that we get a result, the length of the result should be the same as prices

# Test with a window size of 1 (should return NaN)
def test_calculate_rsi_with_window_one():
    prices = [44, 46, 47, 45, 43, 42, 44, 45]
    window = 1
    result = calculate_rsi(prices, window=window)
    assert result.isna().all()  # The RSI for a window of 1 should be NaN for all points

# Test with a negative window size
def test_calculate_rsi_with_negative_window():
    prices = [44, 46, 47, 45, 43]
    window = -3
    try:
        calculate_rsi(prices, window=window)
        assert False, "Expected ValueError for negative window size"
    except ValueError as e:
        assert str(e) == "window must be an integer >= 1"