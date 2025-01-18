from unittest.mock import patch, MagicMock

import pytest

from tests.order_execution.mock_data import MOCK_CONFIG_VALUES

# Mock `load_config_values`
with patch("utils.file_utils.load_config_values", return_value=MOCK_CONFIG_VALUES):
    from order_execution.executor_base import sell_coin_for_usdt


# Mock the client and other dependencies
class MockClient:
    @staticmethod
    def new_order_test(symbol, side, type, quantity):
        return {"symbol": symbol, "side": side, "type": type, "quantity": quantity}


@pytest.fixture
def mock_client():
    return MockClient()


def test_sell_coin_for_usdt_successful(mock_client):
    # Test a successful sell transaction
    with patch("order_execution.executor_base.client", mock_client), \
            patch("order_execution.executor_base.check_coin_balance", return_value=10), \
            patch("order_execution.executor_base.extract_and_calculate_quantity", return_value=5), \
            patch("order_execution.executor_base.save_data_to_file") as mock_save_data:
        coins_data = {
            "BTC": {
                "pair_metadata": {
                    "BTCUSDT": {
                        "filters": [
                            {"filterType": "LOT_SIZE", "minQty": "0.001", "maxQty": "1000", "stepSize": "0.001"},
                            {"filterType": "NOTIONAL", "minNotional": "10"}
                        ]
                    }
                }
            }
        }
        wallet_balance = {"BTC": 10}

        sell_coin_for_usdt("BTC", 100, coins_data, wallet_balance)

        # Assertions
        mock_save_data.assert_called_once()  # Verify that the transaction was saved
        args = mock_save_data.call_args[0]
        assert args[0]["quantity"] == 5  # Ensure correct quantity was used
        assert args[0]["side"] == "SELL"


def test_sell_coin_for_usdt_insufficient_balance(mock_client, capsys):
    # Test when the wallet balance is insufficient
    mock_client.ticker_price = MagicMock(return_value={"price": "50000.0"})  # Mock price

    # Test when the wallet balance is insufficient
    with patch("order_execution.executor_base.client", mock_client), \
            patch("order_execution.executor_base.check_coin_balance", return_value=0.0005), \
            patch("order_execution.executor_base.validate_quantity") as mock_validate_quantity, \
            patch("order_execution.executor_base.save_data_to_file"):
        # Mock validate_quantity to raise an error for insufficient balance
        mock_validate_quantity.side_effect = ValueError(
            "Quantity 0.0005 is below the minimum allowed quantity of 0.001")

        coins_data = {
            "BTC": {
                "pair_metadata": {
                    "BTCUSDT": {
                        "filters": [
                            {"filterType": "LOT_SIZE", "minQty": "0.001", "maxQty": "1000", "stepSize": "0.001"},
                            {"filterType": "NOTIONAL", "minNotional": "10"}
                        ]
                    }
                }
            }
        }
        wallet_balance = {"BTC": 0.0005}

        # Call the function and expect it to log the error
        sell_coin_for_usdt("BTC", 100, coins_data, wallet_balance)

        # Capture the printed output
        captured = capsys.readouterr()
        assert "An error occurred while trying to sell BTC" in captured.out
        assert "Quantity 0.0005 is below the minimum allowed quantity of 0.001" in captured.out


def test_sell_coin_for_usdt_invalid_trading_pair(mock_client, capsys):
    # Test when the trading pair is invalid
    with patch("order_execution.executor_base.client", mock_client), \
            patch("order_execution.executor_base.check_coin_balance", return_value=10), \
            patch("order_execution.executor_base.extract_and_calculate_quantity",
                  side_effect=KeyError("Invalid trading pair")), \
            patch("order_execution.executor_base.save_data_to_file"):
        coins_data = {
            "BTC": {
                "pair_metadata": {}  # No trading pair available
            }
        }
        wallet_balance = {"BTC": 10}

        # Call the function and capture the output
        sell_coin_for_usdt("BTC", 100, coins_data, wallet_balance)

        # Capture the printed output
        captured = capsys.readouterr()

        # Assert that the error message includes the KeyError
        assert "An error occurred while trying to sell BTC: 'Invalid trading pair'" in captured.out


def test_sell_coin_for_usdt_order_placement_failure(mock_client, capsys):
    # Test when order placement fails
    with patch("order_execution.executor_base.client", mock_client), \
            patch("order_execution.executor_base.check_coin_balance", return_value=10), \
            patch("order_execution.executor_base.extract_and_calculate_quantity", return_value=5), \
            patch("order_execution.executor_base.client.new_order_test",
                  side_effect=Exception("Order placement failed")), \
            patch("order_execution.executor_base.save_data_to_file"):
        coins_data = {
            "BTC": {
                "pair_metadata": {
                    "BTCUSDT": {
                        "filters": [
                            {"filterType": "LOT_SIZE", "minQty": "0.001", "maxQty": "1000", "stepSize": "0.001"},
                            {"filterType": "NOTIONAL", "minNotional": "10"}
                        ]
                    }
                }
            }
        }
        wallet_balance = {"BTC": 10}

        # Call the function and expect it to log the error
        sell_coin_for_usdt("BTC", 100, coins_data, wallet_balance)

        # Capture the printed output
        captured = capsys.readouterr()

        # Verify the error message is logged
        assert "An error occurred while trying to sell BTC: Order placement failed" in captured.out
