import pytest
from unittest.mock import patch
from tests.order_execution.mock_data import MOCK_CONFIG_VALUES

# Mock `load_config_values`
with patch("utils.file_utils.load_config_values", return_value=MOCK_CONFIG_VALUES):
    from order_execution.executor_base import extract_filter_parameters

def test_extract_filter_parameters_valid_filters():
    # Test with valid filters
    filters = [
        {'filterType': 'LOT_SIZE', 'minQty': '0.01', 'maxQty': '1000', 'stepSize': '0.01'},
        {'filterType': 'NOTIONAL', 'minNotional': '10'}
    ]
    min_qty, max_qty, step_size, min_notional = extract_filter_parameters(filters)

    assert min_qty == 0.01
    assert max_qty == 1000
    assert step_size == 0.01
    assert min_notional == 10


def test_extract_filter_parameters_missing_lot_size_filter():
    # Test with missing 'LOT_SIZE' filter
    filters = [
        {'filterType': 'NOTIONAL', 'minNotional': '10'}
    ]
    with pytest.raises(ValueError, match="'LOT_SIZE' filter not found"):
        extract_filter_parameters(filters)


def test_extract_filter_parameters_missing_notional_filter():
    # Test with missing 'NOTIONAL' filter
    filters = [
        {'filterType': 'LOT_SIZE', 'minQty': '0.01', 'maxQty': '1000', 'stepSize': '0.01'}
    ]
    with pytest.raises(ValueError, match="'NOTIONAL' filter not found"):
        extract_filter_parameters(filters)


def test_extract_filter_parameters_missing_both_filters():
    # Test with missing both 'LOT_SIZE' and 'NOTIONAL' filters
    filters = []
    with pytest.raises(ValueError, match="'LOT_SIZE' filter not found"):
        extract_filter_parameters(filters)


def test_extract_filter_parameters_invalid_min_qty():
    # Test with invalid 'minQty' value (non-numeric)
    filters = [
        {'filterType': 'LOT_SIZE', 'minQty': 'invalid', 'maxQty': '1000', 'stepSize': '0.01'},
        {'filterType': 'NOTIONAL', 'minNotional': '10'}
    ]
    with pytest.raises(ValueError):
        extract_filter_parameters(filters)


def test_extract_filter_parameters_invalid_max_qty():
    # Test with invalid 'maxQty' value (non-numeric)
    filters = [
        {'filterType': 'LOT_SIZE', 'minQty': '0.01', 'maxQty': 'invalid', 'stepSize': '0.01'},
        {'filterType': 'NOTIONAL', 'minNotional': '10'}
    ]
    with pytest.raises(ValueError):
        extract_filter_parameters(filters)


def test_extract_filter_parameters_invalid_step_size():
    # Test with invalid 'stepSize' value (non-numeric)
    filters = [
        {'filterType': 'LOT_SIZE', 'minQty': '0.01', 'maxQty': '1000', 'stepSize': 'invalid'},
        {'filterType': 'NOTIONAL', 'minNotional': '10'}
    ]
    with pytest.raises(ValueError):
        extract_filter_parameters(filters)


def test_extract_filter_parameters_invalid_min_notional():
    # Test with invalid 'minNotional' value (non-numeric)
    filters = [
        {'filterType': 'LOT_SIZE', 'minQty': '0.01', 'maxQty': '1000', 'stepSize': '0.01'},
        {'filterType': 'NOTIONAL', 'minNotional': 'invalid'}
    ]
    with pytest.raises(ValueError):
        extract_filter_parameters(filters)


def test_extract_filter_parameters_empty_filter():
    # Test with empty filter dictionaries (missing necessary keys)
    filters = [
        {'filterType': 'LOT_SIZE'},
        {'filterType': 'NOTIONAL'}
    ]
    with pytest.raises(KeyError):
        extract_filter_parameters(filters)


def test_extract_filter_parameters_mixed_case_filter_types():
    # Test with filters having different cases in 'filterType'
    filters = [
        {'filterType': 'lot_size', 'minQty': '0.01', 'maxQty': '1000', 'stepSize': '0.01'},
        {'filterType': 'notional', 'minNotional': '10'}
    ]
    with pytest.raises(ValueError, match="'LOT_SIZE' filter not found"):
        extract_filter_parameters(filters)