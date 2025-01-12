import pandas as pd
from utils.file_utils import load_config_values

config = load_config_values("MOMENTUM_INDICATORS")


def calculate_rsi(prices, window=14):
    # Check if prices are provided and have sufficient length
    if not prices or len(prices) < window:
        return None

    # Validate the window parameter
    if not isinstance(window, int) or window < 1:
        raise ValueError("window must be an integer >= 1")

    # If window size is 1, return NaN for all values
    if window == 1:
        return pd.Series([float('nan')] * len(prices))

    # Convert prices to a pandas series
    prices_series = pd.Series(prices)

    # Calculate price differences
    delta = prices_series.diff()

    # Calculate gains (positive differences) and losses (negative differences)
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

    # Calculate relative strength (RS) and RSI
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    return rsi

def calculate_stochastic_oscillator(highs, lows, closes, window=14, smooth_window=3):
    if len(highs) < window or len(lows) < window or len(closes) < window:
        return None

    # Validate the window parameter
    if not isinstance(window, int) or window < 2:
        raise ValueError("window must be an integer >= 2")

    highest_high = pd.Series(highs).rolling(window=window).max()
    lowest_low = pd.Series(lows).rolling(window=window).min()
    percent_k = ((pd.Series(closes) - lowest_low) / (highest_high - lowest_low)) * 100
    percent_d = percent_k.rolling(window=smooth_window).mean()  # Smoothed %K

    return {
        '%K': percent_k,
        '%D': percent_d
    }

def calculate_williams_r(highs, lows, closes, window=14):
    if len(highs) < window or len(lows) < window or len(closes) < window:
        return None

    # Validate the window parameter
    if not isinstance(window, int) or window < 2:
        raise ValueError("window must be an integer >= 2")

    highest_high = pd.Series(highs).rolling(window=window).max()
    lowest_low = pd.Series(lows).rolling(window=window).min()
    williams_r = ((highest_high - pd.Series(closes)) / (highest_high - lowest_low)) * -100

    return williams_r

def calculate_cci(highs, lows, closes, window=20):
    if len(highs) < window or len(lows) < window or len(closes) < window:
        return None

    # Validate the window parameter
    if not isinstance(window, int) or window < 2:
        raise ValueError("window must be an integer >= 2")

    # Calculate Typical Price (TP) = (High + Low + Close) / 3
    typical_price = (pd.Series(highs) + pd.Series(lows) + pd.Series(closes)) / 3

    # Calculate SMA of Typical Price
    tp_sma = typical_price.rolling(window=window).mean()

    # Calculate Mean Deviation (manually)
    mean_deviation = typical_price.rolling(window=window).apply(
        lambda x: pd.Series(x).sub(x.mean()).abs().mean(), raw=False
    )

    # Calculate CCI
    cci = (typical_price - tp_sma) / (0.015 * mean_deviation)

    return cci

def calculate_momentum_indicators(high_prices, low_prices, close_prices):
    indicators = {}
    try:
        # Relative Strength Index (RSI)
        rsi_period = config['MOMENTUM_INDICATORS']['RSI_WINDOW']
        if len(close_prices) >= rsi_period:
            indicators['RSI'] = calculate_rsi(close_prices, rsi_period)

        # Stochastic Oscillator
        stochastic_config = config['MOMENTUM_INDICATORS']['STOCHASTIC']
        stochastic_window = stochastic_config['WINDOW']
        smooth_window = stochastic_config['SMOOTH_WINDOW']
        if len(high_prices) >= stochastic_window and len(low_prices) >= stochastic_window and len(close_prices) >= stochastic_window:
            indicators['StochasticOscillator'] = calculate_stochastic_oscillator(
                high_prices, low_prices, close_prices, stochastic_window, smooth_window
            )

        # Williams %R
        williams_r_window = config['MOMENTUM_INDICATORS']['WILLIAMS_R_WINDOW']
        if len(high_prices) >= williams_r_window and len(low_prices) >= williams_r_window and len(close_prices) >= williams_r_window:
            indicators['Williams%R'] = calculate_williams_r(
                high_prices, low_prices, close_prices, williams_r_window
            )

        # Commodity Channel Index (CCI)
        cci_window = config['MOMENTUM_INDICATORS']['CCI_WINDOW']
        if len(high_prices) >= cci_window and len(low_prices) >= cci_window and len(close_prices) >= cci_window:
            indicators['CCI'] = calculate_cci(
                high_prices, low_prices, close_prices, cci_window
            )

    except Exception as e:
        print(f"Error in calculating momentum indicators: {e}")

    return indicators


def simplify_momentum_indicators(momentum_indicators):
    simplified = {}

    # RSI: Extract the latest value and add thresholds
    if "RSI" in momentum_indicators and momentum_indicators["RSI"] is not None:
        rsi_series = momentum_indicators["RSI"]
        if not rsi_series.empty:
            simplified["RSI"] = rsi_series.iloc[-1]
            # Determine RSI signal (oversold, overbought, or neutral)
            if simplified["RSI"] < 30:
                simplified["RSI_signal"] = "oversold"
            elif simplified["RSI"] > 70:
                simplified["RSI_signal"] = "overbought"
            else:
                simplified["RSI_signal"] = "neutral"

    # Stochastic Oscillator: Include overbought/oversold signals
    if "StochasticOscillator" in momentum_indicators and momentum_indicators["StochasticOscillator"] is not None:
        stochastic = momentum_indicators["StochasticOscillator"]

        if "%K" in stochastic and "%D" in stochastic:
            # Safely retrieve the latest value of %K and %D
            simplified["Stochastic_%K"] = (
                stochastic["%K"].iloc[-1] if not stochastic["%K"].empty else None
            )
            simplified["Stochastic_%D"] = (
                stochastic["%D"].iloc[-1] if not stochastic["%D"].empty else None
            )

            # Check if the latest %K indicates an overbought or oversold condition
            if simplified["Stochastic_%K"] is not None:
                if simplified["Stochastic_%K"] < 20:
                    simplified["Stochastic_signal"] = "oversold"
                elif simplified["Stochastic_%K"] > 80:
                    simplified["Stochastic_signal"] = "overbought"
                else:
                    simplified["Stochastic_signal"] = "neutral"

    # Williams %R: Add signal for overbought/oversold conditions
    if "Williams%R" in momentum_indicators and momentum_indicators["Williams%R"] is not None:
        williams_r_series = momentum_indicators["Williams%R"]
        if not williams_r_series.empty:
            simplified["Williams%R"] = williams_r_series.iloc[-1]
            simplified["Williams%R_signal"] = (
                "oversold" if simplified["Williams%R"] > -20
                else "overbought" if simplified["Williams%R"] < -80
                else "neutral"
            )

    # Commodity Channel Index (CCI)
    if "CCI" in momentum_indicators and momentum_indicators["CCI"] is not None:
        cci_series = momentum_indicators["CCI"]
        if not cci_series.empty:
            simplified["CCI"] = cci_series.iloc[-1]
            simplified["CCI_signal"] = (
                "overbought" if simplified["CCI"] > 100
                else "oversold" if simplified["CCI"] < -100
                else "neutral"
            )

    return simplified