import pytest
from unittest.mock import patch

# Mock `load_config_values` before importing the target module
# NOTE: Changing those will impact the test results
mock_config_values = {
    "PRICE_CHANGE_THRESHOLD": 2,
    "PRICE_RANGE_VOLATILITY_THRESHOLD": 0.05,
}

with patch("utils.file_utils.load_config_values", return_value=mock_config_values):
    from services.data_fetcher import fetch_all_symbols_data

with patch("utils.file_utils.load_config_values", return_value=mock_config_values):
    from services.data_fetcher import filter_potential_coins

with patch("utils.file_utils.load_config_values", return_value=mock_config_values):
    from services.data_fetcher import fetch_coins_data


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

def test_filter_potential_coins():
    # Mock input data for the `filter_potential_coins` function
    mock_all_symbols_data = {
        "exchange_info": {
            "symbols": [
                {"symbol": "BTCUSDT", "baseAsset": "BTC", "quoteAsset": "USDT"},
                {"symbol": "ETHUSDT", "baseAsset": "ETH", "quoteAsset": "USDT"},
                {"symbol": "XRPUSDT", "baseAsset": "XRP", "quoteAsset": "USDT"}
            ]
        },
        "active_symbols": {"BTCUSDT", "ETHUSDT"},
        "stats": [
            {"symbol": "BTCUSDT", "priceChangePercent": "6", "highPrice": "52000", "lowPrice": "49000"},
            {"symbol": "ETHUSDT", "priceChangePercent": "4", "highPrice": "4200", "lowPrice": "4000"},
            {"symbol": "XRPUSDT", "priceChangePercent": "12", "highPrice": "1.1", "lowPrice": "0.9"}
        ]
    }

    # Call the function under test
    result = filter_potential_coins(mock_all_symbols_data)

    # Expected result based on the provided mock data and thresholds
    expected_result = {"BTC"}  # BTCUSDT meets both thresholds

    # Assertions
    assert result == expected_result, f"Expected {expected_result}, but got {result}"

def test_fetch_coins_data(mock_client):
    # Mock input for all_symbols_data
    mock_all_symbols_data = {
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
            {"symbol": "BTCUSDT", "priceChangePercent": "5"},
            {"symbol": "ETHUSDT", "priceChangePercent": "3"},
            {"symbol": "BTCETH", "priceChangePercent": "2"}
        ]
    }

    # Mock client behavior for candlestick data
    mock_candlesticks = [
        [1639040400000, "50000.00", "51000.00", "49000.00", "50500.00", "1000"],
        [1639044000000, "50500.00", "51500.00", "49500.00", "51000.00", "800"]
    ]
    mock_client.klines.return_value = mock_candlesticks

    # Coins to fetch data for
    potential_and_wallet_coins = ["BTC", "ETH"]

    # Call the function under test
    result = fetch_coins_data(mock_all_symbols_data, potential_and_wallet_coins)

    # Assertions
    assert "BTC" in result
    assert "ETH" in result

    # Validate BTC data
    btc_data = result["BTC"]
    assert btc_data["pairings"] == ["BTCUSDT", "BTCETH"]
    assert btc_data["real_time_prices"]["BTCUSDT"] == 50000.0
    assert btc_data["real_time_prices"]["BTCETH"] == 12.5
    assert btc_data["market_stats"]["BTCUSDT"]["priceChangePercent"] == "5"
    assert btc_data["market_stats"]["BTCETH"]["priceChangePercent"] == "2"
    assert btc_data["candlesticks"]["BTCUSDT"] == mock_candlesticks

    # Validate ETH data
    eth_data = result["ETH"]
    assert eth_data["pairings"] == ["ETHUSDT", "BTCETH"]
    assert eth_data["real_time_prices"]["ETHUSDT"] == 4000.0
    assert eth_data["real_time_prices"]["BTCETH"] == 12.5
    assert eth_data["market_stats"]["ETHUSDT"]["priceChangePercent"] == "3"
    assert eth_data["market_stats"]["BTCETH"]["priceChangePercent"] == "2"
    assert eth_data["candlesticks"]["BTCETH"] == mock_candlesticks