from unittest.mock import patch

import numpy as np

from tests.indicators.mock_data import MOCK_CONFIG_VALUES

# Mock `load_config_values`
with patch("utils.file_utils.load_config_values", return_value=MOCK_CONFIG_VALUES):
    from indicators.indicator_base import clean_indicators


def test_clean_indicators_converts_float64():
    test_input = {'value': np.float64(53.325714285714284)}
    expected_output = {'value': 53.3257}

    result = clean_indicators(test_input)

    assert result == expected_output


def test_clean_indicators_converts_float32():
    test_input = {'value': np.float32(53.325714285714284)}
    expected_output = {'value': 53.3257}

    result = clean_indicators(test_input)

    assert result == expected_output


def test_clean_indicators_converts_int64():
    test_input = {'value': np.int64(100)}
    expected_output = {'value': 100}

    result = clean_indicators(test_input)

    assert result == expected_output


def test_clean_indicators_converts_int32():
    test_input = {'value': np.int32(100)}
    expected_output = {'value': 100}

    result = clean_indicators(test_input)

    assert result == expected_output


def test_clean_indicators_converts_bool_True():
    test_input = {'value': np.bool_(True)}
    expected_output = {'value': True}

    result = clean_indicators(test_input)

    assert result == expected_output


def test_clean_indicators_converts_bool_False():
    test_input = {'value': np.bool_(False)}
    expected_output = {'value': False}

    result = clean_indicators(test_input)

    assert result == expected_output


def test_clean_indicators_converts_nested_dict():
    test_input = {
        'outer': {
            'inner': np.float64(5.6789),
            'another': np.int64(42)
        }
    }
    expected_output = {
        'outer': {
            'inner': 5.6789,
            'another': 42
        }
    }

    result = clean_indicators(test_input)

    assert result == expected_output


def test_clean_indicators_converts_list():
    test_input = {'values': [np.float64(1.2345), np.int64(100)]}
    expected_output = {'values': [1.2345, 100]}

    result = clean_indicators(test_input)

    assert result == expected_output


def test_clean_indicators_converts_float():
    test_input = {'value': 12.34567}
    expected_output = {'value': 12.3457}

    result = clean_indicators(test_input)

    assert result == expected_output


def test_clean_indicators_no_conversion_needed():
    test_input = {'value': 'string'}
    expected_output = {'value': 'string'}

    result = clean_indicators(test_input)

    assert result == expected_output
