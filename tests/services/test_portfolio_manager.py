from unittest.mock import patch

import pytest

from services.wallet_info import extract_balance, fetch_wallet_balance


def test_extract_balance_with_valid_data():
    wallet_info = {
        "balances": [
            {"asset": "BTC", "free": "0.01", "locked": "0.00"},
            {"asset": "ETH", "free": "0.0", "locked": "1.5"},
            {"asset": "XRP", "free": "0.0", "locked": "0.0"},  # Should be excluded
            {"asset": "USDT", "free": "100.0", "locked": "0.0"},  # Special case
        ]
    }

    prices = [
        {"symbol": "BTCUSDT", "price": "50000.0"},
        {"symbol": "ETHUSDT", "price": "2000.0"},
    ]

    # Mock Binance client
    with patch("services.binance_auth.client.ticker_price", return_value=prices):
        result = extract_balance(wallet_info)

        # Assert the result is calculated correctly
        assert len(result) == 3  # XRP should be excluded

        # ETH should come first because it has the highest value in USDT
        assert result[0]["asset"] == "ETH"
        assert result[0]["value_in_usdt"] == 1.5 * 2000.0
        assert result[0]["percentage"] == pytest.approx(83.33, rel=1e-2)

        # BTC comes next because it has a higher value than USDT
        assert result[1]["asset"] == "BTC"
        assert result[1]["value_in_usdt"] == 0.01 * 50000.0
        assert result[1]["percentage"] == pytest.approx(13.89, rel=1e-2)

        # USDT should be the last because it has the lowest value
        assert result[2]["asset"] == "USDT"
        assert result[2]["value_in_usdt"] == 100.0
        assert result[2]["percentage"] == pytest.approx(2.78, rel=1e-2)


def test_extract_balance_with_no_balances():
    wallet_info = {
        "balances": []  # Empty balances
    }

    prices = []

    # Mock Binance client
    with patch("services.binance_auth.client.ticker_price", return_value=prices):
        result = extract_balance(wallet_info)

        # Assert that result is empty
        assert result == []


@patch("services.portfolio_manager.client")
def test_fetch_wallet_balance(mock_client):
    # Mock `account` response
    mock_client.account.return_value = {
        "balances": [
            {"asset": "BTC", "free": "0.01", "locked": "0.00"},
            {"asset": "USDT", "free": "100.0", "locked": "0.0"},
        ]
    }

    # Mock `ticker_price` response
    mock_client.ticker_price.return_value = [
        {"symbol": "BTCUSDT", "price": "50000.0"},
    ]

    # Call the function
    result = fetch_wallet_balance()

    # Assert wallet balance is returned correctly
    assert len(result) == 2
    assert result[0]["asset"] == "BTC"
    assert result[0]["value_in_usdt"] == 0.01 * 50000.0
    assert result[1]["asset"] == "USDT"
    assert result[1]["value_in_usdt"] == 100.0
