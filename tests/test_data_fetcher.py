# tests/test_data_fetcher.py

import pytest
from services.data_fetcher import fetch_all_symbols_data
from unittest.mock import patch


@pytest.fixture
def mock_client():
    with patch("services.binance_auth.client") as mock_client:
        yield mock_client


def test_fetch_all_symbols_data_returns_correct_keys(mock_client):
    mock_client.exchange_info.return_value = {"symbols": [{"symbol": "BTCUSDT", "status": "TRADING"}]}
    mock_client.ticker_price.return_value = [{"symbol": "BTCUSDT", "price": "50000"}]
    mock_client.ticker_24hr.return_value = [{"symbol": "BTCUSDT", "24h_volume": "100"}]

    result = fetch_all_symbols_data()
    assert set(result.keys()) == {"exchange_info", "active_symbols", "prices", "stats"}


def test_fetch_all_symbols_data_filters_active_symbols(mock_client):
    mock_client.exchange_info.return_value = {
        "symbols": [
            {"symbol": "BTCUSDT", "status": "TRADING"},
            {"symbol": "ETHUSDT", "status": "INACTIVE"},
        ]
    }
    mock_client.ticker_price.return_value = [{"symbol": "BTCUSDT", "price": "50000"}]
    mock_client.ticker_24hr.return_value = [{"symbol": "BTCUSDT", "24h_volume": "100"}]

    result = fetch_all_symbols_data()
    assert result["active_symbols"] == {"BTCUSDT"}
    assert all(item["symbol"] == "BTCUSDT" for item in result["prices"])
    assert all(item["symbol"] == "BTCUSDT" for item in result["stats"])


def test_fetch_all_symbols_data_handles_empty_data(mock_client):
    mock_client.exchange_info.return_value = {"symbols": []}
    mock_client.ticker_price.return_value = []
    mock_client.ticker_24hr.return_value = []

    result = fetch_all_symbols_data()
    assert result["active_symbols"] == set()
    assert result["prices"] == []
    assert result["stats"] == []


def test_fetch_all_symbols_data_calls_client_methods(mock_client):
    mock_client.exchange_info.return_value = {"symbols": []}
    mock_client.ticker_price.return_value = []
    mock_client.ticker_24hr.return_value = []

    fetch_all_symbols_data()

    mock_client.exchange_info.assert_called_once()
    mock_client.ticker_price.assert_called_once()
    mock_client.ticker_24hr.assert_called_once()
