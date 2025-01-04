import pandas as pd


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

    def calculate_sma(self, prices, window=14):
        """
        Calculate Simple Moving Average (SMA).

        :param prices: List or array of prices.
        :param window: Number of periods for SMA calculation.
        :return: SMA values as a pandas Series.
        """
        if not prices:
            return None
        prices_series = pd.Series(prices)
        return prices_series.rolling(window=window).mean()

    def calculate_ema(self, prices, window=14):
        """
        Calculate Exponential Moving Average (EMA).

        :param prices: List or array of prices.
        :param window: Number of periods for EMA calculation.
        :return: EMA values as a pandas Series.
        """
        if not prices:
            return None
        prices_series = pd.Series(prices)
        return prices_series.ewm(span=window, adjust=False).mean()

    def calculate_rsi(self, prices, window=14):
        """
        Calculate Relative Strength Index (RSI).

        :param prices: List or array of prices.
        :param window: Number of periods for RSI calculation.
        :return: RSI values as a pandas Series.
        """
        if not prices or len(prices) < window:
            return None
        prices_series = pd.Series(prices)
        delta = prices_series.diff()

        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

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
                sma_14 = self.calculate_sma(close_prices, window=14).round(8).tolist()
                ema_14 = self.calculate_ema(close_prices, window=14).round(8).tolist()
                rsi_14 = self.calculate_rsi(close_prices, window=14).round(2).tolist()

                # Store indicators in dictionary
                indicators[coin] = {
                    "sma_14": sma_14,
                    "ema_14": ema_14,
                    "rsi_14": rsi_14,
                }

            except Exception as e:
                print(f"Error calculating indicators for {coin}: {e}")

        return indicators