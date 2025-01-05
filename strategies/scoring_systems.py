DEFAULT_SCORING_SYSTEM = "scoring_system_5"

def get_active_scoring_system(indicators):
    scoring_systems = {
        "scoring_system_1": scoring_system_1,
        "scoring_system_2": scoring_system_2,
        "scoring_system_3": scoring_system_3,
        "scoring_system_4": scoring_system_4,
        "scoring_system_5": scoring_system_5,
        "scoring_system_6": scoring_system_6,
        "scoring_system_7": scoring_system_7,
    }
    return scoring_systems[DEFAULT_SCORING_SYSTEM](indicators)


def scoring_system_1(indicators):
    rsi_score = indicators['momentum']['RSI'] * 1.2
    sma_score_weighted = indicators['trend']['SMA'] * -1.8
    macd_score = indicators['trend']['MACD_histogram'] * 2.5
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
    bollinger_width_score = indicators['volatility']['bollinger_width'] * 0.7
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
    sma_deviation_score = -abs(indicators['trend']['SMA_deviation']) * 1.8
    bollinger_deviation_score = -abs(indicators['volatility']['Bollinger_deviation']) * 2.7
    rsi_score = indicators['momentum']['RSI'] * 1.3
    raw_score = sma_deviation_score + bollinger_deviation_score + rsi_score
    return max(-100, min(100, raw_score / 1.8))

def scoring_system_7(indicators):
    stochastic_score = 8 if indicators['momentum']['Stochastic_signal'] == "bullish" else -8
    momentum_score = (indicators['momentum']['RSI'] * 1.8 + stochastic_score) * indicators['momentum']['market_condition_factor']
    volatility_score = (-0.8 * indicators['volatility']['ATR']) * (1.8 - indicators['momentum']['market_condition_factor'])
    trend_score = indicators['trend']['SMA'] * -0.8 * indicators['momentum']['market_condition_factor']
    raw_score = momentum_score + volatility_score + trend_score
    return max(-100, min(100, raw_score / 2))