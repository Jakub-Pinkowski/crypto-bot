from services.data_fetcher import get_coins_data
from indicators.indicator_base import calculate_indicators
from strategies.base_strategy import analyze_coins

if __name__ == "__main__":
    # Fetch coins data and wallet balance
    coins_data, wallet_balance = get_coins_data()

    # Calculate indicators for each coin
    coins_indicators = calculate_indicators(coins_data)

    # Analyze the indicators for each coin
    coins_to_trade = analyze_coins(coins_indicators)