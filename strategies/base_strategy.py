from strategies.scoring_systems import get_active_scoring_system
from utils.file_utils import save_data_to_file

def analyze_coins(indicators):
    """
    Analyze indicators, rank coins, and determine buy/sell/hold actions for the portfolio.

    If conditions for trading (buy/sell) are not met, the bot will recommend holding.

    :param indicators: A dictionary containing all indicators for each coin.

    Configure scoring function code added (call scoring functions).
        Return dict comes separately tightly wrapped most conditions eliminated clarified
    """
    analyzed_coins = {}
    rankings = []

    for coin, coin_indicators in indicators.items():
        # Calculate composite score
        score = get_active_scoring_system(coin_indicators)

        # Append coin and score to rankings
        rankings.append((coin, score))

        # Default action for this coin
        analyzed_coins[coin] = {
            "action": "HOLD",  # Default action unless decided otherwise
            "reason": [],
            "score": score  # Include score for transparency
        }

    # Rank coins by score
    rankings.sort(key=lambda x: x[1], reverse=True)

    # Define the threshold
    score_threshold = 2.0

    # Decision-making based on rankings
    if len(rankings) > 1:
        best_coin, best_score = rankings[0]
        worst_coin, worst_score = rankings[-1]

        # Check if the score difference exceeds the threshold
        score_gap = best_score - worst_score
        if score_gap >= score_threshold:
            # Signal to buy the most attractive coin
            analyzed_coins[best_coin]["action"] = "BUY"
            analyzed_coins[best_coin]["reason"].append(
                f"Highest attractiveness score ({best_score:.2f})."
            )

            # Signal to sell the least attractive coin
            analyzed_coins[worst_coin]["action"] = "SELL"
            analyzed_coins[worst_coin]["reason"].append(
                f"Lowest attractiveness score ({worst_score:.2f})."
            )
        else:
            # If the score gap is too small, hold the portfolio
            for coin in analyzed_coins:
                analyzed_coins[coin]["action"] = "HOLD"
                analyzed_coins[coin]["reason"].append(
                    f"Score difference too small ({score_gap:.2f}), no significant action taken."
                )
    else:
        # If there's only one coin in the portfolio, no trading can occur
        for coin in analyzed_coins:
            analyzed_coins[coin]["action"] = "HOLD"
            analyzed_coins[coin]["reason"].append("Only one coin available, holding.")

    # Sort analysis by score (best to worst) before saving
    sorted_analysis = dict(sorted(analyzed_coins.items(), key=lambda item: item[1]["score"], reverse=True))
    save_data_to_file(sorted_analysis, "analysis_data", "analysis_data")

    return analyzed_coins
