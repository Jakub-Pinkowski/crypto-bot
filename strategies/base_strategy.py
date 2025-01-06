from strategies.scoring_systems import calculate_score
from utils.file_utils import save_data_to_file

def rank_coins(indicators):
    rankings = []

    for coin, coin_indicators in indicators.items():
        # Calculate composite score
        score = calculate_score(coin_indicators)

        # Append coin and score to rankings
        rankings.append({"coin": coin, "score": score})

    # Rank coins by score in descending order
    rankings.sort(key=lambda x: x["score"], reverse=True)

    return rankings

def analyze_coins(indicators):
    # Get the sorted rankings
    ranked_coins = rank_coins(indicators)

    # Identify coin to buy (highest score) and coin to sell (lowest score)
    coin_to_buy = ranked_coins[0] if ranked_coins else None  # Highest score
    coin_to_sell = ranked_coins[-1] if ranked_coins else None  # Lowest score

    # Consolidate highest and lowest score coins into coins_to_trade
    coins_to_trade = {
        "coin_to_buy": coin_to_buy,
        "coin_to_sell": coin_to_sell
    }

    # Save the ranked coins
    save_data_to_file(ranked_coins, "analysis", "ranked_coins")  # Save rankings

    return coins_to_trade
