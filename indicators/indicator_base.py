import json
import os
from datetime import datetime
import numpy as np

from indicators.trend_indicators import calculate_sma, calculate_ema, calculate_macd, calculate_ichimoku_cloud
from indicators.momentum_indicators import  calculate_rsi, calculate_stochastic_oscillator, calculate_williams_r, calculate_cci
from indicators.volatility_indicators import calculate_bollinger_bands, calculate_atr

def calculate_indicators(coins_data):
    strategy = IncidatorBase(coins_data)
    print("Calculating indicators...")

    # Apply all indicators to data and return only indicators
    indicators = strategy.apply_indicators()

    return indicators


class IncidatorBase:
    def __init__(self, coins_data):
        # TODO: Add a description

        self.coins_data = coins_data

    def extract_ohlc_prices(self, coin):
        """
        Extract high, low, and close prices from the candlestick (OHLCV) data.

        Parameters:
            coin (str): The name of the coin for which to extract prices.

        Returns:
            tuple: (high_prices, low_prices, close_prices), each as a list of floats.
        """
        candlestick_data = self.coins_data[coin].get("candlesticks", {})

        # Lists to store prices
        high_prices = []
        low_prices = []
        close_prices = []

        for pair, data_list in candlestick_data.items():
            high_prices.extend([float(ohlcv[2]) for ohlcv in data_list])  # index 2 is the high price
            low_prices.extend([float(ohlcv[3]) for ohlcv in data_list])  # index 3 is the low price
            close_prices.extend([float(ohlcv[4]) for ohlcv in data_list])  # index 4 is the close price

        return high_prices, low_prices, close_prices

    def calculate_trend_indicators(self, high_prices, low_prices, close_prices):
        indicators = {}
        try:
            # Simple Moving Average (SMA)
            sma_period = 14
            indicators['SMA'] = calculate_sma(close_prices, sma_period)

            # Exponential Moving Average (EMA)
            ema_period = 14
            indicators['EMA'] = calculate_ema(close_prices, ema_period)

            # MACD
            indicators['MACD'] = calculate_macd(close_prices)

            # Calculate Ichimoku Cloud
            indicators['Ichimoku'] = calculate_ichimoku_cloud(high_prices, low_prices, close_prices)

        except Exception as e:
            print(f"Error in calculating basic indicators: {e}")

        return indicators

    def calculate_momentum_indicators(self, high_prices, low_prices, close_prices):
        indicators = {}
        try:
            # Relative Strength Index (RSI)
            rsi_period = 14
            indicators['RSI'] = calculate_rsi(close_prices, rsi_period)

            # Stochastic Oscillator
            stochastic_window = 14
            indicators['StochasticOscillator'] = calculate_stochastic_oscillator(
                high_prices, low_prices, close_prices, stochastic_window
            )

            # Williams %R
            williams_r_window = 14
            indicators['Williams%R'] = calculate_williams_r(
                high_prices, low_prices, close_prices, williams_r_window
            )

            # Commodity Channel Index (CCI)
            cci_window = 20
            indicators['CCI'] = calculate_cci(
                high_prices, low_prices, close_prices, cci_window
            )

        except Exception as e:
            print(f"Error in calculating momentum indicators: {e}")

        return indicators

    def calculate_volatility_indicators(self, high_prices, low_prices, close_prices):
        indicators = {}
        try:
            # Bollinger Bands
            indicators['BollingerBands'] = calculate_bollinger_bands(close_prices)

            # Average True Range (ATR)
            atr_period = 14
            indicators['ATR'] = calculate_atr(high_prices, low_prices, close_prices, atr_period)

        except Exception as e:
            print(f"Error in calculating advanced indicators: {e}")

        return indicators

    def simplify_trend_indicators(self, trend_indicators, close_prices):
        """
        Simplifies trend indicators by extracting actionable data.
        """
        simplified = {}

        # Extract the latest value for each trend indicator
        if "SMA" in trend_indicators:
            simplified["SMA"] = trend_indicators["SMA"].iloc[-1]  # Latest SMA value

            # Check if close price is above or below the SMA
            simplified["above_SMA"] = close_prices[-1] > simplified["SMA"]

        if "EMA" in trend_indicators:
            simplified["EMA"] = trend_indicators["EMA"].iloc[-1]  # Latest EMA value

        # MACD: Add signal direction (e.g., bullish or bearish crossover)
        if "MACD" in trend_indicators and trend_indicators["MACD"]:
            macd_data = trend_indicators["MACD"]

            # Safely extract MACD components
            simplified["MACD_current"] = macd_data["macd_line"].iloc[-1] if "macd_line" in macd_data else None
            simplified["MACD_signal"] = macd_data["signal_line"].iloc[-1] if "signal_line" in macd_data else None
            simplified["MACD_histogram"] = macd_data["histogram"].iloc[-1] if "histogram" in macd_data else None

            # Determine the trend based on MACD and Signal line values
            if simplified["MACD_current"] and simplified["MACD_signal"]:
                simplified["MACD_trend"] = (
                    "bullish" if simplified["MACD_current"] > simplified["MACD_signal"] else "bearish"
                )

        else:
            print(f"No valid MACD data for trend simplification.")


        return simplified

    def simplify_momentum_indicators(self, momentum_indicators):
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

    def simplify_volatility_indicators(self, volatility_indicators, close_prices):
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

    def clean_indicators(self, indicators):
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


    def save_indicators_to_file(self, indicators, filename=None):
        """
        Saves indicators to a JSON file in the indicators_data folder.

        Parameters:
            indicators (dict): The data to be saved.
            filename (str, optional): File name for the saved data. Uses timestamp by default.

        Returns:
            Nothing
        """
        # Default file name with timestamp if none is provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"indicators_{timestamp}.json"

        # Ensure the indicators_data folder exists
        base_dir = os.path.dirname(os.path.dirname(__file__))  # Navigate to project root
        directory = os.path.join(base_dir, "data", "indicators_data")
        os.makedirs(directory, exist_ok=True)  # Ensure target directory exists

        # Save the data as JSON
        file_path = os.path.join(directory, filename)
        with open(file_path, "w") as file:
            json.dump(indicators, file, indent=4)

        print(f"Indicators data saved to {file_path}")

    def apply_indicators(self):
        indicators = {}  # To store indicators for each coin

        for coin, data in self.coins_data.items():
            try:
                # Extract high, low, close prices
                high_prices, low_prices, close_prices = self.extract_ohlc_prices(coin)

                # Validate there are enough prices for indicator calculation
                if len(close_prices) < 2:
                    print(f"Not enough close prices for {coin}, skipping...")
                    continue

                # Calculate trend indicators
                trend_indicators = self.calculate_trend_indicators(high_prices, low_prices, close_prices)

                # Calculate momentum indicators
                momentum_indicators = self.calculate_momentum_indicators(high_prices, low_prices, close_prices)

                # Calculate volatility indicators
                volatility_indicators = self.calculate_volatility_indicators(high_prices, low_prices, close_prices)

                # **Simplify** the data into the latest value or actionable signals
                simplified_trend = self.simplify_trend_indicators(trend_indicators, close_prices)
                simplified_momentum = self.simplify_momentum_indicators(momentum_indicators)
                simplified_volatility = self.simplify_volatility_indicators(volatility_indicators, close_prices)

                # Combine simplified indicators into the final structure
                indicators[coin] = {
                    'trend': simplified_trend,
                    'momentum': simplified_momentum,
                    'volatility': simplified_volatility
                }

            except Exception as e:
                print(f"Error calculating indicators for {coin}: {e}")

        # Create a cleaned version of the indicators
        cleaned_indicators = self.clean_indicators(indicators)

        # Save indicators to a file
        self.save_indicators_to_file(cleaned_indicators)

        # Return the cleaned_indicators
        return cleaned_indicators

