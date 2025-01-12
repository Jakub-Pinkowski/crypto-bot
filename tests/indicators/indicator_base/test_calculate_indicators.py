import pytest
from unittest.mock import patch
from tests.indicators.mock_data import MOCK_CONFIG_VALUES

# Mock `load_config_values`
with patch("utils.file_utils.load_config_values", return_value=MOCK_CONFIG_VALUES):
    from indicators.indicator_base import calculate_indicators

# Mock data for coins_data
coins_data = {
    "BTC": {
        "candlesticks": {
            "1h": [
                [1633072800, 45000, 46000, 44000, 45000],
                [1633076400, 45500, 46500, 44500, 46000],
            ]
        }
    }
}

# Mock cleaned indicators after apply_indicators and clean_indicators
cleaned_indicators_mock = {
    "BTC": {
        "trend": "up",
        "momentum": 50,
        "volatility": 5
    }
}

def test_calculate_indicators_calls_apply_indicators():
    with patch("indicators.indicator_base.apply_indicators") as mock_apply_indicators:
        # Mock the return value of apply_indicators
        mock_apply_indicators.return_value = cleaned_indicators_mock

        # Call the function
        result = calculate_indicators(coins_data)

        # Assert that apply_indicators was called with the correct coins_data
        mock_apply_indicators.assert_called_once_with(coins_data)


def test_calculate_indicators_calls_clean_indicators():
    with patch("indicators.indicator_base.apply_indicators", return_value=cleaned_indicators_mock), \
            patch("indicators.indicator_base.clean_indicators",
                  return_value=cleaned_indicators_mock) as mock_clean_indicators:
        # Call the function
        result = calculate_indicators(coins_data)

        # Assert that clean_indicators was called with the output from apply_indicators
        mock_clean_indicators.assert_called_once_with(cleaned_indicators_mock)

# TODO: Fix this one test
def test_calculate_indicators_calls_save_data_to_file():
    with patch("indicators.indicator_base.apply_indicators", return_value=cleaned_indicators_mock), \
            patch("indicators.indicator_base.clean_indicators", return_value=cleaned_indicators_mock), \
            patch("utils.file_utils.save_data_to_file") as mock_save_data_to_file:
        # Call the function
        result = calculate_indicators(coins_data)

        # Assert that save_data_to_file was called with the correct arguments
        mock_save_data_to_file.assert_called_once_with(cleaned_indicators_mock, "indicators", "indicators")


def test_calculate_indicators_returns_cleaned_indicators():
    with patch("indicators.indicator_base.apply_indicators", return_value=cleaned_indicators_mock), \
            patch("indicators.indicator_base.clean_indicators", return_value=cleaned_indicators_mock):
        # Call the function
        result = calculate_indicators(coins_data)

        # Assert that the function returns the cleaned indicators
        assert result == cleaned_indicators_mock


def test_calculate_indicators_handles_exception():
    # Mocking the functions to raise an exception
    with patch("indicators.indicator_base.apply_indicators", side_effect=Exception("Error in apply_indicators")):
        # Call the function and assert it doesn't raise an error
        with pytest.raises(Exception, match="Error in apply_indicators"):
            calculate_indicators(coins_data)