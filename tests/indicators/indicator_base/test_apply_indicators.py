from unittest.mock import patch

from tests.indicators.mock_data import MOCK_CONFIG_VALUES

# Mock `load_config_values`
with patch("utils.file_utils.load_config_values", return_value=MOCK_CONFIG_VALUES):
    from indicators.indicator_base import apply_indicators


def test_apply_indicators_success():
    # Mock coins_data for testing
    coins_data = {
        "BTC": {
            "candlesticks": {
                "1h": [
                    [1633072800, 45000, 46000, 44000, 45000],
                    [1633076400, 45500, 46500, 44500, 46000],
                    [1633080000, 46000, 47000, 45000, 46500],
                ]
            }
        }
    }

    # Assuming the calculation functions return mock values
    with patch("indicators.indicator_base.calculate_trend_indicators", return_value={'trend': 'up'}), \
            patch("indicators.indicator_base.calculate_momentum_indicators", return_value={'momentum': 50}), \
            patch("indicators.indicator_base.calculate_volatility_indicators", return_value={'volatility': 5}), \
            patch("indicators.indicator_base.simplify_trend_indicators", return_value='up'), \
            patch("indicators.indicator_base.simplify_momentum_indicators", return_value=50), \
            patch("indicators.indicator_base.simplify_volatility_indicators", return_value=5):
        # Call the function with mock data
        indicators = apply_indicators(coins_data)

        # Assert that the indicators are calculated and structured correctly
        assert "BTC" in indicators
        assert "trend" in indicators["BTC"]
        assert "momentum" in indicators["BTC"]
        assert "volatility" in indicators["BTC"]
        assert indicators["BTC"]['trend'] == 'up'
        assert indicators["BTC"]['momentum'] == 50
        assert indicators["BTC"]['volatility'] == 5


def test_apply_indicators_missing_close_prices():
    # Mock coins_data where close prices are not enough
    coins_data = {
        "BTC": {
            "candlesticks": {
                "1h": [
                    [1633072800, 45000, 46000, 44000, 45000]  # Only one close price
                ]
            }
        }
    }

    # Call the function
    indicators = apply_indicators(coins_data)

    # Assert that no indicators were calculated for BTC because of insufficient close prices
    assert "BTC" not in indicators


def test_apply_indicators_error_handling():
    # Mock coins_data for testing
    coins_data = {
        "BTC": {
            "candlesticks": {
                "1h": [
                    [1633072800, 45000, 46000, 44000, 45000],
                    [1633076400, 45500, 46500, 44500, 46000],
                ]
            }
        }
    }

    # Simulate an exception during calculation (e.g., in trend calculation)
    with patch("indicators.indicator_base.calculate_trend_indicators", side_effect=Exception("Calculation error")):
        with patch("indicators.indicator_base.calculate_momentum_indicators", return_value={'momentum': 50}), \
                patch("indicators.indicator_base.calculate_volatility_indicators", return_value={'volatility': 5}), \
                patch("indicators.indicator_base.simplify_trend_indicators", return_value='up'), \
                patch("indicators.indicator_base.simplify_momentum_indicators", return_value=50), \
                patch("indicators.indicator_base.simplify_volatility_indicators", return_value=5):
            # Call the function
            indicators = apply_indicators(coins_data)

            # Assert that no indicators are calculated for BTC due to error in trend calculation
            assert "BTC" not in indicators


def test_apply_indicators_empty_data():
    # Call the function with empty data
    coins_data = {}
    indicators = apply_indicators(coins_data)

    # Assert that the return value is an empty dictionary
    assert indicators == {}


def test_apply_indicators_coin_without_candlesticks():
    # Mock coins_data where 'ETH' has no 'candlesticks' data
    coins_data = {
        "BTC": {
            "candlesticks": {
                "1h": [
                    [1633072800, 45000, 46000, 44000, 45000],
                    [1633076400, 45500, 46500, 44500, 46000],
                ]
            }
        },
        "ETH": {}  # ETH has no candlestick data
    }

    # Call the function
    indicators = apply_indicators(coins_data)

    # Assert that indicators for BTC are present, but ETH is skipped
    assert "BTC" in indicators
    assert "ETH" not in indicators


def test_apply_indicators_empty_candlestick_data():
    # Mock coins_data where the candlesticks are empty
    coins_data = {
        "BTC": {
            "candlesticks": {
                "1h": []  # No candlestick data available
            }
        }
    }

    # Call the function
    indicators = apply_indicators(coins_data)

    # Assert that the coin should be skipped due to lack of candlestick data
    assert "BTC" not in indicators


def test_apply_indicators_multiple_coins():
    # Mock coins_data for multiple coins
    coins_data = {
        "BTC": {
            "candlesticks": {
                "1h": [
                    [1633072800, 45000, 46000, 44000, 45000],
                    [1633076400, 45500, 46500, 44500, 46000],
                ]
            }
        },
        "ETH": {
            "candlesticks": {
                "1h": [
                    [1633072800, 3000, 3100, 2900, 3050],
                    [1633076400, 3100, 3200, 3000, 3150],
                ]
            }
        }
    }

    # Assuming the calculation functions return mock values
    with patch("indicators.indicator_base.calculate_trend_indicators", return_value={'trend': 'up'}), \
            patch("indicators.indicator_base.calculate_momentum_indicators", return_value={'momentum': 50}), \
            patch("indicators.indicator_base.calculate_volatility_indicators", return_value={'volatility': 5}), \
            patch("indicators.indicator_base.simplify_trend_indicators", return_value='up'), \
            patch("indicators.indicator_base.simplify_momentum_indicators", return_value=50), \
            patch("indicators.indicator_base.simplify_volatility_indicators", return_value=5):
        # Call the function with mock data
        indicators = apply_indicators(coins_data)

        # Assert that the indicators for both BTC and ETH are calculated
        assert "BTC" in indicators
        assert "ETH" in indicators
        assert indicators["BTC"]['trend'] == 'up'
        assert indicators["ETH"]['momentum'] == 50


def test_apply_indicators_large_data():
    # Mock coins_data with a large number of coins and candlestick entries
    coins_data = {
        f"COIN{i}": {
            "candlesticks": {
                "1h": [
                    [1633072800, 45000 + i, 46000 + i, 44000 + i, 45000 + i] for i in range(1000)  # 1000 candlesticks
                ]
            }
        } for i in range(10)  # 10 coins
    }

    # Call the function with mock data
    indicators = apply_indicators(coins_data)

    # Assert that the function can handle the large dataset without errors
    assert len(indicators) == 10  # Check that indicators for all coins are returned


def test_apply_indicators_non_numeric_values():
    # Mock coins_data where some candlestick values are non-numeric
    coins_data = {
        "BTC": {
            "candlesticks": {
                "1h": [
                    [1633072800, 45000, 46000, "corrupted", 45000],  # Non-numeric value
                    [1633076400, 45500, 46500, 44500, 46000],
                ]
            }
        }
    }

    # Call the function
    indicators = apply_indicators(coins_data)

    # Assert that the BTC coin is skipped due to the corrupted data
    assert "BTC" not in indicators


def test_apply_indicators_invalid_coin_structure():
    # Mock coins_data with an invalid structure (missing 'candlesticks')
    coins_data = {
        "BTC": {
            "prices": [45000, 46000, 45500],  # Missing 'candlesticks'
        }
    }

    # Call the function
    indicators = apply_indicators(coins_data)

    # Assert that BTC is skipped due to invalid structure
    assert "BTC" not in indicators
