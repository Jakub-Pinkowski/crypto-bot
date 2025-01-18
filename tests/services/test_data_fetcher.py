from unittest.mock import patch

import pytest

from tests.services.mock_data import (
    MOCK_CONFIG_VALUES,
    MOCK_EXCHANGE_INFO,
    MOCK_PRICES,
    MOCK_STATS,
    MOCK_ALL_SYMBOLS_DATA,
    MOCK_CANDLESTICKS,
    MOCK_WALLET_BALANCE,
    MOCK_COINS_DATA
)

# Mock `load_config_values` globally for all imports
with patch("utils.file_utils.load_config_values", return_value=MOCK_CONFIG_VALUES):
    from services.data_fetcher import (
        fetch_all_symbols_data,
        filter_potential_coins,
        fetch_coins_data,
        get_coins_data,
    )


@pytest.fixture
def mock_client():
    """Fixture to mock the 'client' object."""
    with patch("services.data_fetcher.client") as mock_client:
        yield mock_client


def test_fetch_all_symbols_data(mock_client):
    # Assign global mocks
    mock_client.exchange_info.return_value = MOCK_EXCHANGE_INFO
    mock_client.ticker_price.return_value = MOCK_PRICES
    mock_client.ticker_24hr.return_value = MOCK_STATS

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


def test_filter_potential_coins():
    # Call the function under test
    result = filter_potential_coins(MOCK_ALL_SYMBOLS_DATA)

    # Expected result based on the provided mock data and thresholds
    expected_result = {"BTC"}  # BTCUSDT meets both thresholds

    # Assertions
    assert result == expected_result, f"Expected {expected_result}, but got {result}"


def test_fetch_coins_data(mock_client):
    # Assign global mocks
    mock_client.klines.return_value = MOCK_CANDLESTICKS

    # Coins to fetch data for
    potential_and_wallet_coins = ["BTC", "ETH"]

    # Call the function under test
    result = fetch_coins_data(MOCK_ALL_SYMBOLS_DATA, potential_and_wallet_coins)

    # Assertions
    assert "BTC" in result
    assert "ETH" in result

    # Validate BTC data
    btc_data = result["BTC"]
    assert btc_data["pairings"] == ["BTCUSDT", "BTCETH"]
    assert btc_data["real_time_prices"]["BTCUSDT"] == 50000.0
    assert btc_data["real_time_prices"]["BTCETH"] == 12.5

    btc_market_stat = next(stat for stat in MOCK_ALL_SYMBOLS_DATA["stats"] if stat["symbol"] == "BTCUSDT")
    assert btc_market_stat["priceChangePercent"] == "6"
    assert btc_market_stat["highPrice"] == "52000"
    assert btc_market_stat["lowPrice"] == "49000"
    assert btc_data["candlesticks"]["BTCUSDT"] == MOCK_CANDLESTICKS

    # Validate ETH data
    eth_data = result["ETH"]
    assert eth_data["pairings"] == ["ETHUSDT", "BTCETH"]
    assert eth_data["real_time_prices"]["ETHUSDT"] == 4000.0
    assert eth_data["real_time_prices"]["BTCETH"] == 12.5

    eth_market_stat = next(stat for stat in MOCK_ALL_SYMBOLS_DATA["stats"] if stat["symbol"] == "ETHUSDT")
    assert eth_market_stat["priceChangePercent"] == "4"
    assert eth_market_stat["highPrice"] == "4200"
    assert eth_market_stat["lowPrice"] == "4000"

    assert eth_data["candlesticks"]["ETHUSDT"] == MOCK_CANDLESTICKS


@patch("services.data_fetcher.fetch_all_symbols_data", return_value=MOCK_ALL_SYMBOLS_DATA)
@patch("services.data_fetcher.filter_potential_coins", return_value={"BTC"})
@patch("services.data_fetcher.fetch_wallet_balance", return_value=MOCK_WALLET_BALANCE)
@patch("services.data_fetcher.fetch_coins_data", return_value=MOCK_COINS_DATA)
@patch("services.data_fetcher.save_data_to_file")
def test_get_coins_data(
        mock_save_data_to_file, mock_fetch_coins_data, mock_fetch_wallet_balance, mock_filter_potential_coins,
        mock_fetch_all_symbols_data
):
    # Call the function under test
    result, wallet_balance = get_coins_data()

    # Assertions for each function
    mock_fetch_all_symbols_data.assert_called_once()
    mock_filter_potential_coins.assert_called_once_with(MOCK_ALL_SYMBOLS_DATA)
    mock_fetch_wallet_balance.assert_called_once()
    expected_combined_coins = {"BTC", "ETH"}
    mock_fetch_coins_data.assert_called_once_with(MOCK_ALL_SYMBOLS_DATA, expected_combined_coins)
    mock_save_data_to_file.assert_called_once_with(MOCK_COINS_DATA, "market", "coins_data")

    # Validate returned data
    assert result == MOCK_COINS_DATA
    assert wallet_balance == MOCK_WALLET_BALANCE
