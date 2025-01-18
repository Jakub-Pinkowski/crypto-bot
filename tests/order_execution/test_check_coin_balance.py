from unittest.mock import patch

import pytest

from tests.order_execution.mock_data import MOCK_CONFIG_VALUES

# Mock `load_config_values`
with patch("utils.file_utils.load_config_values", return_value=MOCK_CONFIG_VALUES):
    from order_execution.executor_base import check_coin_balance


def test_check_coin_balance_valid_coin():
    wallet_balance = [
        {'asset': 'BTC', 'free': '1.23'},
        {'asset': 'ETH', 'free': '2.34'},
    ]
    result = check_coin_balance(wallet_balance, 'BTC')
    assert result == 1.23


def test_check_coin_balance_valid_coin_different_case():
    wallet_balance = [
        {'asset': 'btc', 'free': '0.5'},
        {'asset': 'ETH', 'free': '1.0'},
    ]
    result = check_coin_balance(wallet_balance, 'btc')
    assert result == 0.5


def test_check_coin_balance_coin_not_in_wallet():
    wallet_balance = [
        {'asset': 'BTC', 'free': '1.23'},
        {'asset': 'ETH', 'free': '2.34'},
    ]
    with pytest.raises(ValueError, match="ADA notfound in wallet."):
        check_coin_balance(wallet_balance, 'ADA')


def test_check_coin_balance_empty_wallet():
    wallet_balance = []
    with pytest.raises(ValueError, match="BTC notfound in wallet."):
        check_coin_balance(wallet_balance, 'BTC')


def test_check_coin_balance_zero_balance():
    wallet_balance = [
        {'asset': 'BTC', 'free': '0.00'},
        {'asset': 'ETH', 'free': '2.34'},
    ]
    result = check_coin_balance(wallet_balance, 'BTC')
    assert result == 0.00


def test_check_coin_balance_invalid_free_value():
    wallet_balance = [
        {'asset': 'BTC', 'free': 'invalid'},
        {'asset': 'ETH', 'free': '2.34'},
    ]
    with pytest.raises(ValueError):
        check_coin_balance(wallet_balance, 'BTC')
