import pytest
import math
from unittest.mock import patch
from tests.order_execution.mock_data import MOCK_CONFIG_VALUES

# Mocking the necessary methods and data
MOCK_COINS_DATA = {
    'BTC': {
        'pair_metadata': {
            'BTCUSDT': {
                'filters': [
                    {'filterType': 'LOT_SIZE', 'minQty': '0.001', 'maxQty': '100.0', 'stepSize': '0.001'}
                ]
            }
        }
    },
    'ETH': {
        'pair_metadata': {
            'ETHUSDT': {
                'filters': [
                    {'filterType': 'LOT_SIZE', 'minQty': '0.01', 'maxQty': '1000.0', 'stepSize': '0.01'}
                ]
            }
        }
    }
}

MOCK_PRICE = {'price': '10000'}

# Mock `load_config_values`
with patch("utils.file_utils.load_config_values", return_value=MOCK_CONFIG_VALUES):
    from order_execution.executor_base import extract_and_calculate_quantity


# Mocking the `client.ticker_price` to return MOCK_PRICE dynamically
def test_extract_and_calculate_quantity_valid_case():
    coins_data = MOCK_COINS_DATA

    # Test with dynamic current price (mocked)
    amount_to_use = 10

    # Mock `client.ticker_price` call to return the price dynamically
    with patch('services.binance_auth.client.ticker_price', return_value=MOCK_PRICE):
        # Calculate the expected quantity based on the mocked price
        current_price = float(MOCK_PRICE['price'])
        expected_quantity = amount_to_use / current_price  # Expected is 2.0 since 10000 / 5000 = 2.0

        # Now, calculate the rounded quantity based on step size
        step_size = 0.001
        quantity = math.floor(expected_quantity / step_size) * step_size

        # Now, perform the actual test with the function
        result = extract_and_calculate_quantity('BTC', 'BTCUSDT', coins_data, amount_to_use)

        # Assert the result matches the calculated quantity
        assert result == quantity, f"Expected {quantity}, but got {result}"