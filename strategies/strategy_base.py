from strategies.trend_indicators import calculate_sma, calculate_ema, calculate_macd, calculate_ichimoku_cloud
from strategies.momentum_indicators import  calculate_rsi
from strategies.volatility_indicators import calculate_bollinger_bands

def calculate_indicators(coins_data):
    strategy = StrategyBase(coins_data)
    print("Calculating indicators...")

    # Apply all indicators to data and return only indicators
    indicators = strategy.apply_indicators()

    return indicators


class StrategyBase:
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

    def calculate_momentum_indicators(self, close_prices):
        indicators = {}
        try:
            # Relative Strength Index (RSI)
            rsi_period = 14
            indicators['RSI'] = calculate_rsi(close_prices, rsi_period)

        except Exception as e:
            print(f"Error in calculating advanced indicators: {e}")

        return indicators

    def calculate_volatility_indicators(self, close_prices):
        indicators = {}
        try:
            # Bollinger Bands
            indicators['BollingerBands'] = calculate_bollinger_bands(close_prices)

        except Exception as e:
            print(f"Error in calculating advanced indicators: {e}")

        return indicators

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
                momentum_indicators = self.calculate_momentum_indicators(close_prices)

                # Calculate volatility indicators
                volatility_indicators = self.calculate_volatility_indicators(close_prices)

                # Combine all indicators together
                indicators[coin] = {
                    'trend': trend_indicators,
                    'momentum': momentum_indicators,
                    'volatility': volatility_indicators
                }

            except Exception as e:
                print(f"Error calculating indicators for {coin}: {e}")

        print(f"indicators: {indicators}")
        return indicators