import json
import os
from datetime import datetime
from strategies.scoring_systems import scoring_system_1, scoring_system_2, scoring_system_3

def save_analysis_to_file(analysis, filename=None):
    """
    Saves the analysis results to a JSON file in the analysis_data folder, sorted by score.

    Parameters:
        analysis (dict): The data to be saved (analysis results).
        filename (str, optional): File name for the saved data. Defaults to timestamped name.

    Returns:
        Nothing
    """
    # Default file name with timestamp if none is provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_{timestamp}.json"

    # Ensure the analysis_data folder exists
    base_dir = os.path.dirname(os.path.dirname(__file__))  # Navigate to project root
    directory = os.path.join(base_dir, "data", "analysis_data")
    os.makedirs(directory, exist_ok=True)  # Create the folder if it doesn't exist

    # Sort analysis by score (best to worst)
    sorted_analysis = dict(sorted(analysis.items(), key=lambda item: item[1]["score"], reverse=True))

    # Save the analysis data as JSON
    file_path = os.path.join(directory, filename)
    with open(file_path, "w") as file:
        json.dump(sorted_analysis, file, indent=4)

    print(f"Analysis saved to {file_path}")

def analyze_coins(indicators):
    """
    Analyze indicators, rank coins, and determine buy/sell/hold actions for the portfolio.

    If conditions for trading (buy/sell) are not met, the bot will recommend holding.

    :param indicators: A dictionary containing all indicators for each coin.

    :return: A dictionary containing actions for each coin and the reasoning.
    """
    analyzed_coins = {}
    rankings = []

    # Define variables for the scoring system
    score_threshold = 2.0
    scoring_function = scoring_system_1

    for coin, coin_indicators in indicators.items():
        # Extract relevant indicators
        rsi = coin_indicators["momentum"].get("RSI")
        rsi_penalty = (70 - rsi) if rsi else 0  # Penalize overbought RSI

        sma = coin_indicators["trend"].get("SMA")
        current_price = coin_indicators["trend"].get("current_price", sma)  # Assume SMA if price is missing
        sma_score = (current_price / sma - 1) if sma else 0  # Reward undervalued coins

        macd_histogram = coin_indicators["trend"].get("MACD_histogram", 0)

        # Calculate composite score
        score = scoring_function(rsi_penalty, sma_score, macd_histogram)

        # Append coin and score to rankings
        rankings.append((coin, score))

        # Default action for this coin
        analyzed_coins[coin] = {
            "action": "HOLD",  # Default action unless decided otherwise
            "reason": [],
            "score": score  # Include score for transparency
        }

    # Rank coins by score
    rankings.sort(key=lambda x: x[1], reverse=True)  # Higher score = more attractive

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

    save_analysis_to_file(analyzed_coins)

    return analyzed_coins
