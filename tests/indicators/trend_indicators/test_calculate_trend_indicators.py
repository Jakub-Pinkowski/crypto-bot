import pytest
import pandas as pd
from unittest.mock import patch

# Mock config data
from tests.indicators.mock_data import MOCK_CONFIG_VALUES

@patch("utils.file_utils.load_config_values", return_value=MOCK_CONFIG_VALUES)
def test_calculate_trend_indicators_with_valid_data(mock_load_config):
    # Test with a valid list of prices
    from indicators.trend_indicators import calculate_trend_indicators

    # Generate 52 prices for high, low, and close
    high_prices = list(range(50, 102))  # 50 to 101 inclusive
    low_prices = list(range(40, 92))    # 40 to 91 inclusive
    close_prices = list(range(45, 97))  # 45 to 96 inclusive

    # Call the function
    indicators = calculate_trend_indicators(high_prices, low_prices, close_prices)

    # Validate the indicators are calculated correctly
    assert 'SMA' in indicators
    assert 'EMA' in indicators
    assert 'MACD' in indicators
    assert 'Ichimoku' in indicators

    # Test the returned data type
    assert isinstance(indicators['SMA'], pd.Series)
    assert isinstance(indicators['EMA'], pd.Series)
    assert isinstance(indicators['MACD']['macd_line'], pd.Series)
    assert isinstance(indicators['MACD']['signal_line'], pd.Series)
    assert isinstance(indicators['MACD']['histogram'], pd.Series)
    assert isinstance(indicators['Ichimoku']['tenkan_sen'], pd.Series)
    assert isinstance(indicators['Ichimoku']['kijun_sen'], pd.Series)
    assert isinstance(indicators['Ichimoku']['senkou_span_a'], pd.Series)
    assert isinstance(indicators['Ichimoku']['senkou_span_b'], pd.Series)
    assert isinstance(indicators['Ichimoku']['chikou_span'], pd.Series)

@patch("utils.file_utils.load_config_values", return_value={})
def test_calculate_trend_indicators_with_invalid_config(mock_load_config):
    # Test with missing or invalid configuration
    from indicators.trend_indicators import calculate_trend_indicators

    high_prices = list(range(50, 102))
    low_prices = list(range(40, 92))
    close_prices = list(range(45, 97))

    # Missing or incorrect configuration should raise an exception
    indicators = calculate_trend_indicators(high_prices, low_prices, close_prices)

    # Check if the function gracefully handles missing config values
    assert indicators == {}  # Expected output: empty dictionary

@patch("utils.file_utils.load_config_values", return_value=MOCK_CONFIG_VALUES)
def test_calculate_trend_indicators_with_small_data(mock_load_config):
    # Test with a smaller dataset
    from indicators.trend_indicators import calculate_trend_indicators

    # Smaller dataset
    high_prices = [50, 60, 70]
    low_prices = [40, 50, 60]
    close_prices = [45, 55, 65]

    # Call the function to calculate trend indicators
    indicators = calculate_trend_indicators(high_prices, low_prices, close_prices)

    # Ensure that the indicators that require more data (SMA, EMA, MACD, Ichimoku) are not included
    assert 'SMA' not in indicators  # Not enough data points for SMA
    assert 'EMA' not in indicators  # Not enough data points for EMA
    assert 'MACD' not in indicators  # Not enough data points for MACD
    assert 'Ichimoku' not in indicators  # Not enough data points for Ichimoku

@patch("utils.file_utils.load_config_values", return_value=MOCK_CONFIG_VALUES)
def test_calculate_trend_indicators_with_one_price(mock_load_config):
    # Test with only one price point
    from indicators.trend_indicators import calculate_trend_indicators

    # One price point should still return an empty or NaN result
    high_prices = [50]
    low_prices = [40]
    close_prices = [45]

    indicators = calculate_trend_indicators(high_prices, low_prices, close_prices)

    # Check if the function can handle single data point input
    assert 'SMA' not in indicators
    assert 'EMA' not in indicators
    assert 'MACD' not in indicators
    assert 'Ichimoku' not in indicators

@patch("utils.file_utils.load_config_values", return_value=MOCK_CONFIG_VALUES)
def test_calculate_trend_indicators_with_empty_data(mock_load_config):
    # Test with empty data
    from indicators.trend_indicators import calculate_trend_indicators

    # Empty data should return an empty dictionary
    high_prices = []
    low_prices = []
    close_prices = []

    indicators = calculate_trend_indicators(high_prices, low_prices, close_prices)

    # Ensure no indicators are returned with empty data
    assert indicators == {}