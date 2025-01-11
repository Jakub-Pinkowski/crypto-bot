import pytest
from unittest.mock import patch

# Mock `load_config_values` before importing the target module
mock_config_values = {
    "PRICE_CHANGE_THRESHOLD": 5,
    "PRICE_RANGE_VOLATILITY_THRESHOLD": 0.5,
}

with patch("utils.file_utils.load_config_values", return_value=mock_config_values):
    from services.data_fetcher import fetch_all_symbols_data


@pytest.fixture
def mock_client():
    """Fixture to mock the 'client' object."""
    with patch("services.data_fetcher.client") as mock_client:
        yield mock_client


def test_fetch_all_symbols_data(mock_client):
    # Mock data for client.exchange_info()
    mock_exchange_info = {
        "symbols": [
            {"symbol": "BTCUSDT", "status": "TRADING"},
            {"symbol": "ETHUSDT", "status": "TRADING"},
            {"symbol": "XRPUSDT", "status": "BREAK"},
        ]
    }
    mock_client.exchange_info.return_value = mock_exchange_info

    # Mock data for client.ticker_price()
    mock_prices = [
        {"symbol": "BTCUSDT", "price": "50000"},
        {"symbol": "ETHUSDT", "price": "4000"},
        {"symbol": "XRPUSDT", "price": "1"},
    ]
    mock_client.ticker_price.return_value = mock_prices

    # Mock data for client.ticker_24hr()
    mock_stats = [
        {"symbol": "BTCUSDT", "priceChangePercent": "5"},
        {"symbol": "ETHUSDT", "priceChangePercent": "3"},
        {"symbol": "XRPUSDT", "priceChangePercent": "10"},
    ]
    mock_client.ticker_24hr.return_value = mock_stats

    # Call the function under test
    result = fetch_all_symbols_data()

    # Assertions
    assert "exchange_info" in result
    assert "active_symbols" in result
    assert "prices" in result
    assert "stats" in result

    # Validate that active_symbols only includes trading pairs
    assert result["active_symbols"] == {"BTCUSDT", "ETHUSDT"}

    # Check that the filtered prices only contain active trading pairs
    assert result["prices"] == [
        {"symbol": "BTCUSDT", "price": "50000"},
        {"symbol": "ETHUSDT", "price": "4000"},
    ]

    # Check that the filtered stats only contain active trading pairs
    assert result["stats"] == [
        {"symbol": "BTCUSDT", "priceChangePercent": "5"},
        {"symbol": "ETHUSDT", "priceChangePercent": "3"},
    ]
