import pytest
from unittest.mock import patch

# Global Mock Data
MOCK_CONFIG_VALUES = {
    "PRICE_CHANGE_THRESHOLD": 2,
    "PRICE_RANGE_VOLATILITY_THRESHOLD": 0.05,
}

MOCK_EXCHANGE_INFO = {
    "symbols": [
        {"symbol": "BTCUSDT", "status": "TRADING"},
        {"symbol": "ETHUSDT", "status": "TRADING"},
        {"symbol": "XRPUSDT", "status": "BREAK"},
    ]
}

MOCK_PRICES = [
    {"symbol": "BTCUSDT", "price": "50000"},
    {"symbol": "ETHUSDT", "price": "4000"},
    {"symbol": "XRPUSDT", "price": "1"},
]

MOCK_STATS = [
    {"symbol": "BTCUSDT", "priceChangePercent": "5"},
    {"symbol": "ETHUSDT", "priceChangePercent": "3"},
    {"symbol": "XRPUSDT", "priceChangePercent": "10"},
]

MOCK_ALL_SYMBOLS_DATA = {
    "exchange_info": {
        "symbols": [
            {"symbol": "BTCUSDT", "baseAsset": "BTC", "quoteAsset": "USDT", "baseAssetPrecision": 8,
             "quotePrecision": 2, "filters": []},
            {"symbol": "ETHUSDT", "baseAsset": "ETH", "quoteAsset": "USDT", "baseAssetPrecision": 8,
             "quotePrecision": 2, "filters": []},
            {"symbol": "BTCETH", "baseAsset": "BTC", "quoteAsset": "ETH", "baseAssetPrecision": 8,
             "quotePrecision": 2, "filters": []}
        ]
    },
    "active_symbols": {"BTCUSDT", "ETHUSDT", "BTCETH"},
    "prices": [
        {"symbol": "BTCUSDT", "price": "50000"},
        {"symbol": "ETHUSDT", "price": "4000"},
        {"symbol": "BTCETH", "price": "12.5"}
    ],
    "stats": [
        {"symbol": "BTCUSDT", "priceChangePercent": "6", "highPrice": "52000", "lowPrice": "49000"},
        {"symbol": "ETHUSDT", "priceChangePercent": "4", "highPrice": "4200", "lowPrice": "4000"},
        {"symbol": "XRPUSDT", "priceChangePercent": "12", "highPrice": "1.1", "lowPrice": "0.9"},
    ],
}

MOCK_CANDLESTICKS = [
    [1639040400000, "50000.00", "51000.00", "49000.00", "50500.00", "1000"],
    [1639044000000, "50500.00", "51500.00", "49500.00", "51000.00", "800"],
]

MOCK_WALLET_BALANCE = [
    {"asset": "BTC", "free": "0.5", "locked": "0.1"},
    {"asset": "ETH", "free": "1.0", "locked": "0.0"},
]

MOCK_COINS_DATA = {
    "BTC": {
        "pairings": ["BTCUSDT"],
        "real_time_prices": {"BTCUSDT": 50000.0},
        "market_stats": {"BTCUSDT": {"priceChangePercent": "5"}},
        "candlesticks": {"BTCUSDT": MOCK_CANDLESTICKS},
    },
    "ETH": {
        "pairings": ["ETHUSDT"],
        "real_time_prices": {"ETHUSDT": 4000.0},
        "market_stats": {"ETHUSDT": {"priceChangePercent": "3"}},
        "candlesticks": {"ETHUSDT": MOCK_CANDLESTICKS},
    },
}

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

    # Assertions for fetch_all_symbols_data
    mock_fetch_all_symbols_data.assert_called_once()

    # Assertions for filter_potential_coins
    mock_filter_potential_coins.assert_called_once_with(MOCK_ALL_SYMBOLS_DATA)

    # Assertions for fetch_wallet_balance
    mock_fetch_wallet_balance.assert_called_once()

    # Assertions for fetch_coins_data
    expected_combined_coins = {"BTC", "ETH"}
    mock_fetch_coins_data.assert_called_once_with(MOCK_ALL_SYMBOLS_DATA, expected_combined_coins)

    # Assertions for save_data_to_file
    mock_save_data_to_file.assert_called_once_with(MOCK_COINS_DATA, "market", "coins_data")

    # Validate returned data
    assert result == MOCK_COINS_DATA
    assert wallet_balance == MOCK_WALLET_BALANCE
