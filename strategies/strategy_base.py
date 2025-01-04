import pandas as pd
from strategies.basic_indicators import calculate_sma, calculate_ema, calculate_rsi

def calculate_indicators(coins_data):
    strategy = StrategyBase(coins_data)
    print("Calculating indicators...")

    # Apply all indicators to data and return only indicators
    indicators = strategy.apply_indicators()

    return indicators


class StrategyBase:
    def __init__(self, coins_data):
        """
        Initialize the base strategy class with the given coins data.

        :param coins_data: Dictionary containing all relevant data for coins.
        """
        self.coins_data = coins_data

    def apply_indicators(self):
        """
        Apply all indicators to the coins_data and return only indicators.

        :return: Dictionary containing indicators for each coin.
        """
        indicators = {}  # To store indicators for each coin

        for coin, data in self.coins_data.items():
            try:
                # Extract candlestick data (dictionary of trading pairs)
                candlestick_data = data.get("candlesticks", {})

                # Extract close prices from the relevant trading pair
                close_prices = []
                for pair, data_list in candlestick_data.items():
                    close_prices.extend([float(ohlcv[4]) for ohlcv in data_list])  # index 4 is the close price

                # Validate there are enough prices for indicator calculation
                if len(close_prices) < 2:
                    print(f"Not enough close prices for {coin}, skipping...")
                    continue

                # Calculate indicators
                sma_14 = calculate_sma(close_prices, window=14).round(8).tolist()
                ema_14 = calculate_ema(close_prices, window=14).round(8).tolist()
                rsi_14 = calculate_rsi(close_prices, window=14).round(2).tolist()

                # Store indicators in dictionary
                indicators[coin] = {
                    "sma_14": sma_14,
                    "ema_14": ema_14,
                    "rsi_14": rsi_14,
                }

            except Exception as e:
                print(f"Error calculating indicators for {coin}: {e}")

        return indicators