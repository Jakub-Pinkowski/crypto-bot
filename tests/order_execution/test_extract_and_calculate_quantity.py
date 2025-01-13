import pytest
from unittest.mock import patch
from tests.order_execution.mock_data import MOCK_CONFIG_VALUES

# Mock `load_config_values`
with patch("utils.file_utils.load_config_values", return_value=MOCK_CONFIG_VALUES):
    from order_execution.executor_base import extract_and_calculate_quantity


# Mocked client for testing
class MockClient:
    @staticmethod
    def ticker_price(symbol):
        return {'price': '50.0'}  # Simulate a price response


@pytest.fixture
def mock_client():
    return MockClient()


def test_extract_and_calculate_quantity_valid_no_balance(mock_client):
    # Test when coin_balance is not provided, calculate the quantity based on the amount_to_use
    with patch("order_execution.executor_base.client", mock_client):
        coins_data = {
            'BTC': {
                'pair_metadata': {
                    'BTCUSDT': {
                        'filters': [
                            {'filterType': 'LOT_SIZE', 'minQty': '0.001', 'maxQty': '1000', 'stepSize': '0.001'},
                            {'filterType': 'NOTIONAL', 'minNotional': '10'}
                        ]
                    }
                }
            }
        }

        amount_to_use = 1000
        result = extract_and_calculate_quantity('BTC', 'BTCUSDT', coins_data, amount_to_use)
        assert result == 20.0  # Expected 1000 / 50 = 20.0 rounded to step size 0.001


def test_extract_and_calculate_quantity_with_balance(mock_client):
    # Test when coin_balance is provided, return the minimum of calculated quantity and coin_balance
    with patch("order_execution.executor_base.client", mock_client):
        coins_data = {
            'BTC': {
                'pair_metadata': {
                    'BTCUSDT': {
                        'filters': [
                            {'filterType': 'LOT_SIZE', 'minQty': '0.001', 'maxQty': '1000', 'stepSize': '0.001'},
                            {'filterType': 'NOTIONAL', 'minNotional': '10'}
                        ]
                    }
                }
            }
        }

        amount_to_use = 1000
        coin_balance = 15.0  # Coin balance provided
        result = extract_and_calculate_quantity('BTC', 'BTCUSDT', coins_data, amount_to_use, coin_balance)
        assert result == 15.0  # Since coin_balance is 15.0, return the minimum between calculated and coin_balance


def test_extract_and_calculate_quantity_invalid_quantity_below_min(mock_client):
    # Test when quantity is below the minimum allowed quantity
    with patch("order_execution.executor_base.client", mock_client):
        coins_data = {
            'BTC': {
                'pair_metadata': {
                    'BTCUSDT': {
                        'filters': [
                            {'filterType': 'LOT_SIZE', 'minQty': '0.1', 'maxQty': '1000', 'stepSize': '0.001'},
                            {'filterType': 'NOTIONAL', 'minNotional': '10'}
                        ]
                    }
                }
            }
        }

        amount_to_use = 0  # This should result in a quantity that is below the minQty
        with pytest.raises(ValueError, match="Quantity 0.0 is below the minimum allowed quantity of 0.1"):
            extract_and_calculate_quantity('BTC', 'BTCUSDT', coins_data, amount_to_use)


def test_extract_and_calculate_quantity_invalid_quantity_above_max(mock_client):
    # Test when quantity exceeds the maximum allowed quantity
    with patch("order_execution.executor_base.client", mock_client):
        coins_data = {
            'BTC': {
                'pair_metadata': {
                    'BTCUSDT': {
                        'filters': [
                            {'filterType': 'LOT_SIZE', 'minQty': '0.001', 'maxQty': '1000', 'stepSize': '0.001'},
                            {'filterType': 'NOTIONAL', 'minNotional': '10'}
                        ]
                    }
                }
            }
        }

        amount_to_use = 1000000  # This should result in a quantity above the maxQty
        with pytest.raises(ValueError, match="Quantity 20000.0 exceeds the maximum allowed quantity of 1000"):
            extract_and_calculate_quantity('BTC', 'BTCUSDT', coins_data, amount_to_use)


def test_extract_and_calculate_quantity_invalid_notional(mock_client):
    # Test when the total value is below the minimum notional
    with patch("order_execution.executor_base.client", mock_client):
        coins_data = {
            'BTC': {
                'pair_metadata': {
                    'BTCUSDT': {
                        'filters': [
                            {'filterType': 'LOT_SIZE', 'minQty': '0.001', 'maxQty': '1000', 'stepSize': '0.001'},
                            {'filterType': 'NOTIONAL', 'minNotional': '100'}
                        ]
                    }
                }
            }
        }

        amount_to_use = 1  # This will result in a total value of 1.0, which is below the minNotional
        with pytest.raises(ValueError, match="Total value 1.0 is below the minimum notional value of 100"):
            extract_and_calculate_quantity('BTC', 'BTCUSDT', coins_data, amount_to_use)


def test_extract_and_calculate_quantity_invalid_coin_balance(mock_client):
    # Test when coin_balance is provided but less than the calculated quantity
    with patch("order_execution.executor_base.client", mock_client):
        coins_data = {
            'BTC': {
                'pair_metadata': {
                    'BTCUSDT': {
                        'filters': [
                            {'filterType': 'LOT_SIZE', 'minQty': '0.001', 'maxQty': '1000', 'stepSize': '0.001'},
                            {'filterType': 'NOTIONAL', 'minNotional': '10'}
                        ]
                    }
                }
            }
        }

        amount_to_use = 1000
        coin_balance = 5  # Coin balance less than the calculated quantity
        result = extract_and_calculate_quantity('BTC', 'BTCUSDT', coins_data, amount_to_use, coin_balance)
        assert result == 5.0  # Return the coin_balance since it's less than the calculated quantity


def test_extract_and_calculate_quantity_no_balance(mock_client):
    # Test when coin_balance is None, calculate and return the quantity
    with patch("order_execution.executor_base.client", mock_client):
        coins_data = {
            'BTC': {
                'pair_metadata': {
                    'BTCUSDT': {
                        'filters': [
                            {'filterType': 'LOT_SIZE', 'minQty': '0.001', 'maxQty': '1000', 'stepSize': '0.001'},
                            {'filterType': 'NOTIONAL', 'minNotional': '10'}
                        ]
                    }
                }
            }
        }

        amount_to_use = 1000
        result = extract_and_calculate_quantity('BTC', 'BTCUSDT', coins_data, amount_to_use)
        assert result == 20.0  # Expected 1000 / 50 = 20.0 rounded to step size 0.001