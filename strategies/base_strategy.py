def analyze_coins(indicators):
    """
    Analyzes indicators for each coin and applies a basic trading strategy.
    For now, the strategy uses:
    - RSI: Determines overbought or oversold signals.
    - SMA: Checks for price relative to Simple Moving Average (SMA).

    :param indicators: A dictionary containing all indicators for each coin.
                       Example:
                       {
                           "BTC": {
                               "trend": {"SMA": 45000},
                               "momentum": {"RSI": 25},
                               "volatility": {}
                           },
                           "ETH": {
                               "trend": {"SMA": 2400},
                               "momentum": {"RSI": 75},
                               "volatility": {}
                           }
                       }
    :return: A dictionary containing analysis for each coin.
             Example:
             {
                 "BTC": {
                     "action": "BUY",
                     "reason": ["RSI indicates oversold."],
                     "indicators": {...}
                 },
                 "ETH": {
                     "action": "SELL",
                     "reason": ["RSI indicates overbought."],
                     "indicators": {...}
                 }
             }
    """
    analyzed_coins = {}

    for coin, coin_indicators in indicators.items():
        # Extract relevant indicators
        sma = coin_indicators["trend"].get("SMA")
        rsi = coin_indicators["momentum"].get("RSI")

        # Prepare default analysis structure
        analysis = {
            "action": None,  # Default no action
            "reason": [],  # Reasons behind the action
            "indicators": coin_indicators  # Include all indicators for transparency
        }

        # Apply RSI-based strategy
        if rsi is not None:
            if rsi < 30:  # RSI less than 30 indicates oversold condition
                analysis["action"] = "BUY"
                analysis["reason"].append("RSI indicates oversold.")
            elif rsi > 70:  # RSI greater than 70 indicates overbought condition
                analysis["action"] = "SELL"
                analysis["reason"].append("RSI indicates overbought.")

        # Apply SMA-based strategy
        if sma is not None:
            price = coin_indicators["trend"].get("current_price")  # Assume SMA logic involving current price
            if price is not None:
                if price > sma:
                    if analysis["action"] is None:
                        analysis["action"] = "BUY"
                    analysis["reason"].append("Price is above SMA, indicating upward trend.")
                elif price < sma:
                    if analysis["action"] is None:
                        analysis["action"] = "SELL"
                    analysis["reason"].append("Price is below SMA, indicating downward trend.")

        # Default to HOLD if no actionable signal is determined
        if analysis["action"] is None:
            analysis["action"] = "HOLD"
            analysis["reason"].append("No strong signal for action at this moment.")

        # Add analyzed data for the coin
        analyzed_coins[coin] = analysis

    return analyzed_coins
