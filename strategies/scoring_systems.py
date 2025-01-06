def calculate_score(indicators):
    scoring_systems = [
        scoring_system_1,
        scoring_system_2,
        scoring_system_3,
        scoring_system_4,
        scoring_system_5,
        scoring_system_6,
        scoring_system_7,
        scoring_system_8,
        scoring_system_9,
        scoring_system_10,
    ]

    # Calculate the individual scores for each system
    scores = [scoring_system(indicators) for scoring_system in scoring_systems]

    # Calculate the average score
    final_score = sum(scores) / len(scores)

    return final_score


def scoring_system_1(indicators):
    rsi_score = indicators['momentum']['RSI'] * 1.2
    sma_score_weighted = indicators['trend']['SMA'] * -1.8
    # Check for MACD_histogram and provide fallback
    macd_histogram = indicators['trend'].get('MACD_histogram', 0)
    macd_score = macd_histogram * 2.5
    raw_score = rsi_score + sma_score_weighted + macd_score
    return max(-100, min(100, raw_score / 1.5))

def scoring_system_2(indicators):
    rsi_score = indicators['momentum']['RSI'] * 1.7
    sma_score_weighted = indicators['trend']['SMA'] * -2.5
    raw_score = rsi_score + sma_score_weighted
    return max(-100, min(100, raw_score / 2))

def scoring_system_3(indicators):
    sma_score_weighted = indicators['trend']['SMA'] * -3.5
    rsi_score = indicators['momentum']['RSI'] * 0.8
    raw_score = sma_score_weighted + rsi_score
    return max(-100, min(100, raw_score / 2))

def scoring_system_4(indicators):
    atr_score = indicators['volatility']['ATR'] * -0.8
    sma_score_weighted = indicators['trend']['SMA'] * -1.5
    above_sma_score = 8 if indicators['trend']['above_SMA'] else -8
    bollinger_width_score = indicators['volatility']['Bollinger_width'] * 0.7
    raw_score = atr_score + sma_score_weighted + above_sma_score + bollinger_width_score
    return max(-100, min(100, raw_score / 2))

def scoring_system_5(indicators):
    ema_score = indicators['trend']['EMA'] * (0.8 if indicators['trend']['above_SMA'] else -0.8)
    stochastic_score = 8 if indicators['momentum']['Stochastic_signal'] == "bullish" else -8
    momentum_score = indicators['momentum']['RSI'] * 1.5 + stochastic_score
    volatility_score = indicators['volatility']['ATR'] * -0.7
    raw_score = ema_score + momentum_score + volatility_score
    return max(-100, min(100, raw_score / 1.8))

def scoring_system_6(indicators):
    sma_deviation_score = -abs(indicators['trend']['SMA']) * 1.8
    bollinger_deviation_score = -abs(indicators['volatility']['Bollinger_width']) * 2.7
    rsi_score = indicators['momentum']['RSI'] * 1.3
    raw_score = sma_deviation_score + bollinger_deviation_score + rsi_score
    return max(-100, min(100, raw_score / 1.8))

def scoring_system_7(indicators):
    rsi_score = indicators['momentum']['RSI'] * 1.8
    volatility_score = indicators['volatility']['ATR'] * -0.8
    trend_score = indicators['trend']['SMA'] * -0.8
    raw_score = rsi_score + volatility_score + trend_score
    return max(-100, min(100, raw_score / 2))


def scoring_system_8(indicators):
    macd_trend = indicators['trend'].get('MACD_trend', "neutral")
    macd_histogram = indicators['trend'].get('MACD_histogram', 0)
    macd_trend_score = 10 if macd_trend == "bullish" else (-10 if macd_trend == "bearish" else 0)
    macd_histogram_score = macd_histogram * 3
    rsi_score = (indicators['momentum']['RSI'] - 30) * 1.5
    volatility_score = indicators['volatility']['ATR'] * -0.5
    raw_score = macd_trend_score + macd_histogram_score + rsi_score + volatility_score
    return max(-100, min(100, raw_score / 2))

def scoring_system_9(indicators):
    stochastic_score = (indicators['momentum']['Stochastic_%K'] - indicators['momentum']['Stochastic_%D']) * 2
    ema_score = indicators['trend']['EMA'] * (1.2 if indicators['trend']['above_SMA'] else -1.2)
    stochastic_signal_score = 10 if indicators['momentum']['Stochastic_signal'] == "bullish" else -10
    rsi_score = max(0, (indicators['momentum']['RSI'] - 30)) * 1.1
    raw_score = stochastic_score + ema_score + stochastic_signal_score + rsi_score
    return max(-100, min(100, raw_score / 2.5))

def scoring_system_10(indicators):
    bollinger_position_score = 10 if indicators['volatility']['close_above_upper'] else (
        -10 if indicators['volatility']['close_below_lower'] else 0)
    rsi_score = indicators['momentum']['RSI'] * 1.6
    volatility_penalty = indicators['volatility']['ATR'] * -0.9
    stochastic_score = 5 if indicators['momentum']['Stochastic_signal'] == "bullish" else -5
    raw_score = bollinger_position_score + rsi_score + volatility_penalty + stochastic_score
    return max(-100, min(100, raw_score / 2))
