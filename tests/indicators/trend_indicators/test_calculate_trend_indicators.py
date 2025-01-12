import pytest
import pandas as pd
from unittest.mock import patch

# Mock config data
from tests.indicators.mock_data import MOCK_CONFIG_VALUES

# Mock `load_config_values`
@patch("utils.file_utils.load_config_values", return_value=MOCK_CONFIG_VALUES)
def test_calculate_trend_indicators_with_valid_data(mock_load_config):
    from indicators.trend_indicators import calculate_trend_indicators  # Import inside mock patch

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
