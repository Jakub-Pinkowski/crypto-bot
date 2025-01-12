import pandas as pd
from unittest.mock import patch
from utils.file_utils import load_config_values

# Mock config data
from tests.indicators.mock_data import MOCK_CONFIG_VALUES

@patch("utils.file_utils.load_config_values", return_value=MOCK_CONFIG_VALUES)
def test_calculate_momentum_indicators_with_valid_data(mock_load_config):
    # Test with a valid list of high, low, and close prices
    from indicators.momentum_indicators import calculate_momentum_indicators

    # Generate 52 prices for high, low, and close
    high_prices = list(range(50, 102))  # 50 to 101 inclusive
    low_prices = list(range(40, 92))    # 40 to 91 inclusive
    close_prices = list(range(45, 97))  # 45 to 96 inclusive

    # Call the function
    indicators = calculate_momentum_indicators(high_prices, low_prices, close_prices)

    # Validate the indicators are calculated correctly
    assert 'RSI' in indicators
    assert 'StochasticOscillator' in indicators
    assert 'Williams%R' in indicators
    assert 'CCI' in indicators

    # Test the returned data types
    assert isinstance(indicators['RSI'], pd.Series)
    assert isinstance(indicators['StochasticOscillator'], dict)
    assert isinstance(indicators['StochasticOscillator']['%K'], pd.Series)
    assert isinstance(indicators['StochasticOscillator']['%D'], pd.Series)
    assert isinstance(indicators['Williams%R'], pd.Series)
    assert isinstance(indicators['CCI'], pd.Series)


@patch("utils.file_utils.load_config_values", return_value={})
def test_calculate_momentum_indicators_with_invalid_config(mock_load_config):
    # Test with missing or invalid configuration
    from indicators.momentum_indicators import calculate_momentum_indicators

    high_prices = list(range(50, 102))
    low_prices = list(range(40, 92))
    close_prices = list(range(45, 97))

    # Missing or incorrect configuration should raise an exception
    indicators = calculate_momentum_indicators(high_prices, low_prices, close_prices)

    # Check if the function gracefully handles missing config values
    assert indicators == {}  # Expected output: empty dictionary


@patch("utils.file_utils.load_config_values", return_value=MOCK_CONFIG_VALUES)
def test_calculate_momentum_indicators_with_small_data(mock_load_config):
    # Test with a smaller dataset
    from indicators.momentum_indicators import calculate_momentum_indicators

    # Smaller dataset
    high_prices = [50, 60, 70]
    low_prices = [40, 50, 60]
    close_prices = [45, 55, 65]

    # Call the function to calculate momentum indicators
    indicators = calculate_momentum_indicators(high_prices, low_prices, close_prices)

    # Ensure that the indicators requiring more data (like RSI, CCI, etc.) are not included
    assert 'RSI' not in indicators  # Not enough data points for RSI
    assert 'StochasticOscillator' not in indicators  # Not enough data points for Stochastic Oscillator
    assert 'Williams%R' not in indicators  # Not enough data points for Williams%R
    assert 'CCI' not in indicators  # Not enough data points for CCI


@patch("utils.file_utils.load_config_values", return_value=MOCK_CONFIG_VALUES)
def test_calculate_momentum_indicators_with_one_price(mock_load_config):
    # Test with only one price point
    from indicators.momentum_indicators import calculate_momentum_indicators

    # One price point should still return an empty or NaN result
    high_prices = [50]
    low_prices = [40]
    close_prices = [45]

    indicators = calculate_momentum_indicators(high_prices, low_prices, close_prices)

    # Check if the function can handle single data point input
    assert 'RSI' not in indicators
    assert 'StochasticOscillator' not in indicators
    assert 'Williams%R' not in indicators
    assert 'CCI' not in indicators


@patch("utils.file_utils.load_config_values", return_value=MOCK_CONFIG_VALUES)
def test_calculate_momentum_indicators_with_empty_data(mock_load_config):
    # Test with empty data
    from indicators.momentum_indicators import calculate_momentum_indicators

    # Empty data should return an empty dictionary
    high_prices = []
    low_prices = []
    close_prices = []

    indicators = calculate_momentum_indicators(high_prices, low_prices, close_prices)

    # Ensure no indicators are returned with empty data
    assert indicators == {}