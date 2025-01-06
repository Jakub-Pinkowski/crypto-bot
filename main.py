from services.data_fetcher import get_coins_data
from indicators.indicator_base import calculate_indicators
from strategies.base_strategy import analyze_coins
from services.portfolio_manager import fetch_wallet

if __name__ == "__main__":
    # # Fetch coins data
    # coins_data = get_coins_data()
    #
    # # Calculate indicators for each coin
    # coins_indicators = calculate_indicators(coins_data)
    #
    # # Analyze the indicators for each coin
    # analyzed_coins = analyze_coins(coins_indicators)
    #
    # # Fetch the wallet
    wallet_balance = fetch_wallet()