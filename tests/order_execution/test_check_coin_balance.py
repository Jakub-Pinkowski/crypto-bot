import pytest
from order_execution.executor_base import check_coin_balance


def test_check_coin_balance_valid_coin():
    wallet_balance = [
        {'asset': 'BTC', 'free': '1.23'},
        {'asset': 'ETH', 'free': '2.34'},
    ]
    result = check_coin_balance(wallet_balance, 'BTC')
    assert result == 1.23


def test_check_coin_balance_valid_coin_with_multiple_assets():
    wallet_balance = [
        {'asset': 'BTC', 'free': '1.00'},
        {'asset': 'ETH', 'free': '2.00'},
        {'asset': 'USDT', 'free': '0.50'}
    ]
    result = check_coin_balance(wallet_balance, 'ETH')
    assert result == 2.0


def test_check_coin_balance_invalid_coin():
    wallet_balance = [
        {'asset': 'BTC', 'free': '1.23'},
        {'asset': 'ETH', 'free': '2.34'},
    ]
    with pytest.raises(ValueError, match="DOGE notfound in wallet."):
        check_coin_balance(wallet_balance, 'DOGE')


def test_check_coin_balance_empty_wallet():
    wallet_balance = []
    with pytest.raises(ValueError, match="BTC notfound in wallet."):
        check_coin_balance(wallet_balance, 'BTC')


def test_check_coin_balance_string_value_converted_to_float():
    wallet_balance = [
        {'asset': 'BTC', 'free': '3.50'},
    ]
    result = check_coin_balance(wallet_balance, 'BTC')
    assert isinstance(result, float)
    assert result == 3.5
