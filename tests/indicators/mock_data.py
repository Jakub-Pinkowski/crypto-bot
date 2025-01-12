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
    },
    "MOMENTUM_INDICATORS": {
        "RSI_WINDOW": 14,  # Window for Relative Strength Index
        "STOCHASTIC": {
            "WINDOW": 14,  # Window for the Stochastic Oscillator
            "SMOOTH_WINDOW": 3,  # Smoothing window for %K line
        },
        "WILLIAMS_R_WINDOW": 14,  # Window for Williams %R calculation
        "CCI_WINDOW": 20,  # Window for Commodity Channel Index
    },
    "VOLATILITY_INDICATORS": {
        "BOLLINGER_BANDS": {
            "WINDOW": 20,  # Window for Bollinger Bands
            "NUM_STD_DEV": 2,  # Number of standard deviations for bandwidth
        },
        "ATR_WINDOW": 14,  # Window for Average True Range calculation
    }
}
