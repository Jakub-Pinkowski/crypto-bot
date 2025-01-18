from unittest.mock import patch

from tests.indicators.mock_data import MOCK_CONFIG_VALUES

# Mock `load_config_values`
with patch("utils.file_utils.load_config_values", return_value=MOCK_CONFIG_VALUES):
    from indicators.indicator_base import extract_ohlc_prices


def test_extract_ohlc_prices_success():
    # Mock coins_data with candlesticks data
    coins_data = {
        'DOGE': {
            'candlesticks': {
                'pair1': [
                    [1632328900, 53.5, 54.5, 53.0, 53.3],
                    [1632328960, 53.3, 55.0, 53.1, 54.2]
                ],
                'pair2': [
                    [1632329020, 54.3, 55.1, 53.8, 54.6],
                    [1632329080, 54.6, 55.3, 54.0, 54.9]
                ]
            }
        }
    }

    expected_high_prices = [54.5, 55.0, 55.1, 55.3]
    expected_low_prices = [53.0, 53.1, 53.8, 54.0]
    expected_close_prices = [53.3, 54.2, 54.6, 54.9]

    # Call function
    high_prices, low_prices, close_prices = extract_ohlc_prices(coins_data, 'DOGE')

    # Assert that the output lists match expected values
    assert high_prices == expected_high_prices
    assert low_prices == expected_low_prices
    assert close_prices == expected_close_prices


def test_extract_ohlc_prices_no_candlesticks():
    # Mock coins_data without candlesticks data
    coins_data = {
        'DOGE': {}
    }

    # Call function with missing candlesticks data
    high_prices, low_prices, close_prices = extract_ohlc_prices(coins_data, 'DOGE')

    # Assert that the lists are empty
    assert high_prices == []
    assert low_prices == []
    assert close_prices == []


def test_extract_ohlc_prices_empty_data():
    # Mock coins_data with empty candlesticks data
    coins_data = {
        'DOGE': {
            'candlesticks': {
                'pair1': [],
                'pair2': []
            }
        }
    }

    # Call function with empty candlesticks data
    high_prices, low_prices, close_prices = extract_ohlc_prices(coins_data, 'DOGE')

    # Assert that the lists are empty
    assert high_prices == []
    assert low_prices == []
    assert close_prices == []


def test_extract_ohlc_prices_invalid_data():
    # Mock coins_data with invalid data types in candlesticks
    coins_data = {
        'DOGE': {
            'candlesticks': {
                'pair1': [
                    [1632328900, 53.5, '54.5', 53.0, '53.3'],
                    [1632328960, 53.3, 55.0, 53.1, 54.2]
                ]
            }
        }
    }

    expected_high_prices = [54.5, 55.0]
    expected_low_prices = [53.0, 53.1]
    expected_close_prices = [53.3, 54.2]

    # Call function with mixed data types
    high_prices, low_prices, close_prices = extract_ohlc_prices(coins_data, 'DOGE')

    # Assert that non-float values are correctly converted
    assert high_prices == expected_high_prices
    assert low_prices == expected_low_prices
    assert close_prices == expected_close_prices


def test_extract_ohlc_prices_missing_coin():
    # Mock coins_data without the given coin
    coins_data = {}

    # Call function with a coin that's not in the data
    high_prices, low_prices, close_prices = extract_ohlc_prices(coins_data, 'DOGE')

    # Assert that the lists are empty since the coin doesn't exist in the data
    assert high_prices == []
    assert low_prices == []
    assert close_prices == []
