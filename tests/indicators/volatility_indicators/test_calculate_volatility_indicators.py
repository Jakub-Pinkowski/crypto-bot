from unittest.mock import patch

import pandas as pd

# Mock config data
from tests.indicators.mock_data import MOCK_CONFIG_VALUES


@patch("utils.file_utils.load_config_values", return_value=MOCK_CONFIG_VALUES)
def test_calculate_volatility_indicators_with_valid_data(mock_load_config):
    # Test with a valid list of high, low, and close prices
    from indicators.volatility_indicators import calculate_volatility_indicators

    # Generate 52 prices for high, low, and close
    high_prices = list(range(50, 102))  # 50 to 101 inclusive
    low_prices = list(range(40, 92))  # 40 to 91 inclusive
    close_prices = list(range(45, 97))  # 45 to 96 inclusive

    # Call the function to calculate volatility indicators
    indicators = calculate_volatility_indicators(high_prices, low_prices, close_prices)

    # Validate the indicators are calculated correctly
    assert 'BollingerBands' in indicators
    assert 'ATR' in indicators

    # Test the returned data type
    assert isinstance(indicators['BollingerBands']['middle_band'], pd.Series)
    assert isinstance(indicators['BollingerBands']['upper_band'], pd.Series)
    assert isinstance(indicators['BollingerBands']['lower_band'], pd.Series)
    assert isinstance(indicators['ATR'], pd.Series)


@patch("utils.file_utils.load_config_values", return_value={})
def test_calculate_volatility_indicators_with_invalid_config(mock_load_config):
    # Test with missing or invalid configuration
    from indicators.volatility_indicators import calculate_volatility_indicators

    high_prices = list(range(50, 102))
    low_prices = list(range(40, 92))
    close_prices = list(range(45, 97))

    # Missing or incorrect configuration should return an empty dictionary
    indicators = calculate_volatility_indicators(high_prices, low_prices, close_prices)

    # Check if the function gracefully handles missing config values
    assert indicators == {}  # Expected output: empty dictionary


@patch("utils.file_utils.load_config_values", return_value=MOCK_CONFIG_VALUES)
def test_calculate_volatility_indicators_with_small_data(mock_load_config):
    # Test with a smaller dataset
    from indicators.volatility_indicators import calculate_volatility_indicators

    # Smaller dataset
    high_prices = [50, 60, 70]
    low_prices = [40, 50, 60]
    close_prices = [45, 55, 65]

    # Call the function to calculate volatility indicators
    indicators = calculate_volatility_indicators(high_prices, low_prices, close_prices)

    # Ensure that the indicators that require more data (BollingerBands, ATR) are not included
    assert 'BollingerBands' not in indicators  # Not enough data points for BollingerBands
    assert 'ATR' not in indicators  # Not enough data points for ATR


@patch("utils.file_utils.load_config_values", return_value=MOCK_CONFIG_VALUES)
def test_calculate_volatility_indicators_with_one_price(mock_load_config):
    # Test with only one price point
    from indicators.volatility_indicators import calculate_volatility_indicators

    # One price point should return empty or NaN results for volatility indicators
    high_prices = [50]
    low_prices = [40]
    close_prices = [45]

    indicators = calculate_volatility_indicators(high_prices, low_prices, close_prices)

    # Check if the function can handle single data point input
    assert 'BollingerBands' not in indicators
    assert 'ATR' not in indicators


@patch("utils.file_utils.load_config_values", return_value=MOCK_CONFIG_VALUES)
def test_calculate_volatility_indicators_with_empty_data(mock_load_config):
    # Test with empty data
    from indicators.volatility_indicators import calculate_volatility_indicators

    # Empty data should return an empty dictionary
    high_prices = []
    low_prices = []
    close_prices = []

    indicators = calculate_volatility_indicators(high_prices, low_prices, close_prices)

    # Ensure no indicators are returned with empty data
    assert indicators == {}
