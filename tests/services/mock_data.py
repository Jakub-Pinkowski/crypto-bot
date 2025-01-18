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
