import numpy as np

from indicators.trend_indicators import calculate_trend_indicators, simplify_trend_indicators
from indicators.momentum_indicators import calculate_momentum_indicators
from indicators.volatility_indicators import calculate_volatility_indicators
from utils.file_utils import save_data_to_file

def calculate_indicators(coins_data):
    # Get indicators
    indicators = apply_indicators(coins_data)

    # Clean indicators
    cleaned_indicators = clean_indicators(indicators)

    # Save indicators to a file
    save_data_to_file(cleaned_indicators, "indicators_data", "indicators")

    # Return the cleaned_indicators
    return cleaned_indicators

def extract_ohlc_prices(coins_data, coin):
    candlestick_data = coins_data[coin].get("candlesticks", {})

    # Lists to store prices
    high_prices = []
    low_prices = []
    close_prices = []

    for pair, data_list in candlestick_data.items():
        high_prices.extend([float(ohlcv[2]) for ohlcv in data_list])  # index 2 is the high price
        low_prices.extend([float(ohlcv[3]) for ohlcv in data_list])  # index 3 is the low price
        close_prices.extend([float(ohlcv[4]) for ohlcv in data_list])  # index 4 is the close price

    return high_prices, low_prices, close_prices

def simplify_momentum_indicators(momentum_indicators):
    """
    Simplifies momentum indicators by extracting actionable signals.
    """
    simplified = {}

    # RSI: Extract the latest value and add thresholds
    if "RSI" in momentum_indicators:
        simplified["RSI"] = momentum_indicators["RSI"].iloc[-1]
        simplified["RSI_signal"] = "oversold" if simplified["RSI"] < 30 else (
            "overbought" if simplified["RSI"] > 70 else "neutral"
        )

    # Stochastic Oscillator: Include overbought/oversold signals
    if "StochasticOscillator" in momentum_indicators:
        stochastic = momentum_indicators["StochasticOscillator"]

        if "%K" in stochastic and "%D" in stochastic:
            # Safely retrieve the latest value of %K and %D
            simplified["Stochastic_%K"] = stochastic["%K"].iloc[-1] if not stochastic["%K"].empty else None
            simplified["Stochastic_%D"] = stochastic["%D"].iloc[-1] if not stochastic["%D"].empty else None

            # Check if the latest %K indicates an overbought or oversold condition
            if simplified["Stochastic_%K"] is not None:
                if simplified["Stochastic_%K"] < 20:
                    simplified["Stochastic_signal"] = "oversold"
                elif simplified["Stochastic_%K"] > 80:
                    simplified["Stochastic_signal"] = "overbought"
                else:
                    simplified["Stochastic_signal"] = "neutral"

    return simplified

def simplify_volatility_indicators(volatility_indicators, close_prices):
        """
        Simplifies volatility indicators into actionable insights.
        """
        simplified = {}

        # Bollinger Bands: Extract the width or position relative to the bands
        if "BollingerBands" in volatility_indicators:
            bands = volatility_indicators["BollingerBands"]

            if "upper_band" in bands and "lower_band" in bands and "middle_band" in bands:
                # Calculate the Bollinger Band width
                simplified["Bollinger_width"] = bands["upper_band"].iloc[-1] - bands["lower_band"].iloc[-1]

                # Check if the close price is above or below the bands
                last_close = close_prices[-1]
                simplified["close_above_upper"] = last_close > bands["upper_band"].iloc[-1]
                simplified["close_below_lower"] = last_close < bands["lower_band"].iloc[-1]

        # ATR (Average True Range): Include volatility signal
        if "ATR" in volatility_indicators:
            simplified["ATR"] = volatility_indicators["ATR"].iloc[-1]

        return simplified

def clean_indicators(indicators):
    """
    Convert any NumPy data types in the indicators dictionary
    into standard Python types for clean representation.
    """

    def convert_value(value):
        # Convert NumPy scalars to Python types
        if isinstance(value, (np.float64, np.float32)):
            return round(float(value), 4)  # Convert to Python float and round to 4 decimals
        elif isinstance(value, (np.int64, np.int32, np.int_)):
            return int(value)  # Convert to standard Python int
        elif isinstance(value, np.bool_):
            return bool(value)  # Convert to standard Python bool
        elif isinstance(value, dict):
            # Recursively clean and round nested dictionaries
            return {k: convert_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            # Recursively clean lists
            return [convert_value(v) for v in value]
        elif isinstance(value, float):
            return round(value, 4)  # Round Python native floats
        else:
            # Return the value as is if it doesn't need conversion or rounding
            return value

    # Clean the entire indicators dictionary
    return {coin: convert_value(data) for coin, data in indicators.items()}

def apply_indicators(coins_data):
    indicators = {}

    for coin, data in coins_data.items():
        try:
            # Extract high, low, close prices
            high_prices, low_prices, close_prices = extract_ohlc_prices(coins_data, coin)

            # Validate there are enough prices for indicator calculation
            if len(close_prices) < 2:
                print(f"Not enough close prices for {coin}, skipping...")
                continue

            # Calculate indicators
            trend_indicators = calculate_trend_indicators(high_prices, low_prices, close_prices)
            momentum_indicators = calculate_momentum_indicators(high_prices, low_prices, close_prices)
            volatility_indicators = calculate_volatility_indicators(high_prices, low_prices, close_prices)

            # Simplify the data into the latest value or actionable signals
            simplified_trend = simplify_trend_indicators(trend_indicators, close_prices)
            simplified_momentum = simplify_momentum_indicators(momentum_indicators)
            simplified_volatility = simplify_volatility_indicators(volatility_indicators, close_prices)

            # Combine simplified indicators into the final structure
            indicators[coin] = {
                'trend': simplified_trend,
                'momentum': simplified_momentum,
                'volatility': simplified_volatility
            }

        except Exception as e:
            print(f"Error calculating indicators for {coin}: {e}")

    return indicators


