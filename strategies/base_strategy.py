from strategies.scoring_systems import calculate_score
from utils.file_utils import load_config_values, save_data_to_file

config = load_config_values("BUY_CONDITION", "SELL_CONDITION")


def is_coin_in_wallet(coin, wallet):
    return any(entry["asset"] == coin and entry["free"] > 0 for entry in wallet)


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


# TODO: Update tests
def determine_action(coin, score, wallet_balance):
    # Check if the coin is in the wallet
    coin_in_wallet = is_coin_in_wallet(coin, wallet_balance)

    buy_condition = config["BUY_CONDITION"]
    sell_condition = config["SELL_CONDITION"]

    # SELL condition: Only sell if the coin is in the wallet
    if score < sell_condition:
        if coin_in_wallet:
            return "SELL"
        else:
            return "DO NOT BUY"

    # BUY condition: Always allow buying if the score is high
    if score > buy_condition:
        return "BUY"

    # HOLD condition: Only hold if the coin is in the wallet
    if coin_in_wallet:
        return "HOLD"

    # Default: Don't buy if the coin isn't in the wallet and doesn't qualify for BUY
    return "DO NOT BUY"


def analyze_coins(indicators, wallet_balance):
    # Get the sorted rankings
    ranked_coins = rank_coins(indicators)

    # Initiate the variable
    coin_analysis = []

    for coin_data in ranked_coins:
        coin = coin_data["coin"]
        score = coin_data["score"]

        # Determine action
        action = determine_action(coin, score, wallet_balance)
        coin_analysis.append({"coin": coin, "score": score, "action": action})

    # Save the analysis
    save_data_to_file(coin_analysis, "analysis", "coin_analysis")

    return coin_analysis
