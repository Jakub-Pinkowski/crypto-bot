MOCK_CONFIG_VALUES = {
    "TREND_INDICATORS": {
        "SMA_WINDOW": 14,  # Window for Simple Moving Average
        "EMA_WINDOW": 14,  # Window for Exponential Moving Average
        "MACD": {
            "SHORT_WINDOW": 12,  # Short window for MACD calculation
            "LONG_WINDOW": 26,  # Long window for MACD calculation
            "SIGNAL_WINDOW": 9,  # Signal window for MACD calculation
        },
        "ICHIMOKU": {
            "TENKAN_WINDOW": 9,  # Window for Tenkan-sen (Conversion Line)
            "KIJUN_WINDOW": 26,  # Window for Kijun-sen (Base Line)
            "SENKOU_B_WINDOW": 52,  # Window for Senkou Span B (Leading Span B)
            "SENKOU_SHIFT": 26,  # Forward shift for Senkou spans
        }
    }
}
