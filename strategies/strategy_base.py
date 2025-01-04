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
        # TODO: Add a description

        self.coins_data = coins_data
        
    def extract_close_prices(self, coin):
        # TODO: Add a description

        candlestick_data = self.coins_data[coin].get("candlesticks", {})
        close_prices = []
        for pair, data_list in candlestick_data.items():
            close_prices.extend([float(ohlcv[4]) for ohlcv in data_list])  # index 4 is the close price
    
        return close_prices
        

    def calculate_basic_indicators(self, close_prices):
        indicators = {}
        try:
            # Calculate Simple Moving Average (SMA)
            sma_period = 14
            indicators['SMA'] = calculate_sma(close_prices, sma_period)

            # Calculate Exponential Moving Average (EMA)
            ema_period = 14
            indicators['EMA'] = calculate_ema(close_prices, ema_period)

            # Calculate Relative Strength Index (RSI)
            rsi_period = 14
            indicators['RSI'] = calculate_rsi(close_prices, rsi_period)

        except Exception as e:
            print(f"Error in calculating basic indicators: {e}")

        return indicators

    def apply_indicators(self):
        indicators = {}  # To store indicators for each coin

        for coin, data in self.coins_data.items():
            try:
                # Extract close prices using the new method
                close_prices = self.extract_close_prices(coin)

                # Validate there are enough prices for indicator calculation
                if len(close_prices) < 2:
                    print(f"Not enough close prices for {coin}, skipping...")
                    continue

                # Calculate basic indicators
                basic_indicators = self.calculate_basic_indicators(close_prices)

                # Calculate some other indicator
                # TODO: Implement new indicator group here

                # Combine all indicators together
                indicators[coin] = {
                    'basic': basic_indicators,
                    # Placeholder for additional indicator sections:
                    # 'trends': trend_indicators,
                    # 'advanced': advanced_indicators,
                }

            except Exception as e:
                print(f"Error calculating indicators for {coin}: {e}")

        return indicators