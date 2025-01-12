import pandas as pd
from unittest.mock import patch
from tests.indicators.mock_data import MOCK_CONFIG_VALUES

# Mock `load_config_values`
with patch("utils.file_utils.load_config_values", return_value=MOCK_CONFIG_VALUES):
    from indicators.trend_indicators import calculate_ichimoku_cloud

def test_ichimoku_with_valid_data():
    # Test with valid highs, lows, and closes
    highs = [i + 10 for i in range(60)]
    lows = [i for i in range(60)]
    closes = [i + 5 for i in range(60)]
    result = calculate_ichimoku_cloud(highs, lows, closes)

    highs_series = pd.Series(highs)
    lows_series = pd.Series(lows)
    closes_series = pd.Series(closes)

    # Expected Tenkan-sen
    tenkan_sen = (highs_series.rolling(window=9).max() + lows_series.rolling(window=9).min()) / 2

    # Expected Kijun-sen
    kijun_sen = (highs_series.rolling(window=26).max() + lows_series.rolling(window=26).min()) / 2

    # Expected Senkou Span A
    senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)

    # Expected Senkou Span B
    senkou_span_b = ((highs_series.rolling(window=52).max() +
                      lows_series.rolling(window=52).min()) / 2).shift(26)

    # Expected Chikou Span
    chikou_span = closes_series.shift(-26)

    # Validate results
    pd.testing.assert_series_equal(result['tenkan_sen'], tenkan_sen)
    pd.testing.assert_series_equal(result['kijun_sen'], kijun_sen)
    pd.testing.assert_series_equal(result['senkou_span_a'], senkou_span_a)
    pd.testing.assert_series_equal(result['senkou_span_b'], senkou_span_b)
    pd.testing.assert_series_equal(result['chikou_span'], chikou_span)


def test_ichimoku_with_insufficient_data():
    # Test when the data length is less than the maximum required window
    highs = [10, 20, 30]
    lows = [5, 15, 25]
    closes = [7, 17, 27]
    result = calculate_ichimoku_cloud(highs, lows, closes)
    assert result is None


def test_ichimoku_with_custom_parameters():
    # Test with custom Ichimoku parameters
    highs = [i + 10 for i in range(60)]
    lows = [i for i in range(60)]
    closes = [i + 5 for i in range(60)]
    result = calculate_ichimoku_cloud(highs, lows, closes, tenkan_window=5, kijun_window=10, senkou_b_window=15, senkou_shift=10)

    highs_series = pd.Series(highs)
    lows_series = pd.Series(lows)
    closes_series = pd.Series(closes)

    # Expected Tenkan-sen
    tenkan_sen = (highs_series.rolling(window=5).max() + lows_series.rolling(window=5).min()) / 2

    # Expected Kijun-sen
    kijun_sen = (highs_series.rolling(window=10).max() + lows_series.rolling(window=10).min()) / 2

    # Expected Senkou Span A
    senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(10)

    # Expected Senkou Span B
    senkou_span_b = ((highs_series.rolling(window=15).max() +
                      lows_series.rolling(window=15).min()) / 2).shift(10)

    # Expected Chikou Span
    chikou_span = closes_series.shift(-10)

    # Validate results
    pd.testing.assert_series_equal(result['tenkan_sen'], tenkan_sen)
    pd.testing.assert_series_equal(result['kijun_sen'], kijun_sen)
    pd.testing.assert_series_equal(result['senkou_span_a'], senkou_span_a)
    pd.testing.assert_series_equal(result['senkou_span_b'], senkou_span_b)
    pd.testing.assert_series_equal(result['chikou_span'], chikou_span)


def test_ichimoku_with_empty_data():
    # Test with empty data
    highs = []
    lows = []
    closes = []
    result = calculate_ichimoku_cloud(highs, lows, closes)
    assert result is None


def test_ichimoku_with_negative_values():
    # Test with negative values
    highs = [-i - 10 for i in range(60)]
    lows = [-i for i in range(60)]
    closes = [-i - 5 for i in range(60)]
    result = calculate_ichimoku_cloud(highs, lows, closes)

    highs_series = pd.Series(highs)
    lows_series = pd.Series(lows)
    closes_series = pd.Series(closes)

    # Expected Tenkan-sen
    tenkan_sen = (highs_series.rolling(window=9).max() + lows_series.rolling(window=9).min()) / 2

    # Expected Kijun-sen
    kijun_sen = (highs_series.rolling(window=26).max() + lows_series.rolling(window=26).min()) / 2

    # Expected Senkou Span A
    senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)

    # Expected Senkou Span B
    senkou_span_b = ((highs_series.rolling(window=52).max() +
                      lows_series.rolling(window=52).min()) / 2).shift(26)

    # Expected Chikou Span
    chikou_span = closes_series.shift(-26)

    # Validate results
    pd.testing.assert_series_equal(result['tenkan_sen'], tenkan_sen)
    pd.testing.assert_series_equal(result['kijun_sen'], kijun_sen)
    pd.testing.assert_series_equal(result['senkou_span_a'], senkou_span_a)
    pd.testing.assert_series_equal(result['senkou_span_b'], senkou_span_b)
    pd.testing.assert_series_equal(result['chikou_span'], chikou_span)

def test_ichimoku_with_identical_values():
    # Test with identical highs, lows, and closes
    highs = [50] * 60
    lows = [50] * 60
    closes = [50] * 60
    result = calculate_ichimoku_cloud(highs, lows, closes)

    highs_series = pd.Series(highs)
    lows_series = pd.Series(lows)
    closes_series = pd.Series(closes)

    # Expected Tenkan-sen
    tenkan_sen = (highs_series.rolling(window=9).max() + lows_series.rolling(window=9).min()) / 2

    # Expected Kijun-sen
    kijun_sen = (highs_series.rolling(window=26).max() + lows_series.rolling(window=26).min()) / 2

    # Expected Senkou Span A
    senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)

    # Expected Senkou Span B
    senkou_span_b = ((highs_series.rolling(window=52).max() +
                      lows_series.rolling(window=52).min()) / 2).shift(26)

    # Expected Chikou Span
    chikou_span = closes_series.shift(-26)

    # Validate results
    pd.testing.assert_series_equal(result['tenkan_sen'], tenkan_sen)
    pd.testing.assert_series_equal(result['kijun_sen'], kijun_sen)
    pd.testing.assert_series_equal(result['senkou_span_a'], senkou_span_a)
    pd.testing.assert_series_equal(result['senkou_span_b'], senkou_span_b)
    pd.testing.assert_series_equal(result['chikou_span'], chikou_span)

def test_ichimoku_with_single_data_point():
    # Test with a single data point
    highs = [100]
    lows = [90]
    closes = [95]
    result = calculate_ichimoku_cloud(highs, lows, closes)
    assert result is None  # Should return None due to insufficient data
