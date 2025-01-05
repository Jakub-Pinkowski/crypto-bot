from services.data_fetcher import get_coins_data
from indicators.strategy_base import calculate_indicators

if __name__ == "__main__":
    # Fetch coins data
    coins_data = get_coins_data()

    # Calculate indicators for each coin
    coins_indicators = calculate_indicators(coins_data)
