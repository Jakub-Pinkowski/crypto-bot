import pytest
from unittest.mock import patch
from tests.order_execution.mock_data import MOCK_CONFIG_VALUES

# Mock `load_config_values`
with patch("utils.file_utils.load_config_values", return_value=MOCK_CONFIG_VALUES):
    from order_execution.executor_base import validate_quantity

def test_validate_quantity_valid():
    # Test when quantity is valid and within the allowed range
    result = validate_quantity(10, 1, 100, 20, 100)
    assert result is None  # No exception should be raised


def test_validate_quantity_below_minimum():
    # Test when quantity is below the minimum allowed quantity
    with pytest.raises(ValueError, match="Quantity 0.5 is below the minimum allowed quantity of 1"):
        validate_quantity(0.5, 1, 100, 20, 100)


def test_validate_quantity_above_maximum():
    # Test when quantity exceeds the maximum allowed quantity
    with pytest.raises(ValueError, match="Quantity 150 exceeds the maximum allowed quantity of 100"):
        validate_quantity(150, 1, 100, 20, 100)


def test_validate_total_value_below_minimum_notional():
    # Test when quantity is below the minimum allowed quantity
    with pytest.raises(ValueError, match="Total value 400 is below the minimum notional value of 500"):
        validate_quantity(2, 1, 100, 200, 500)


def test_validate_quantity_valid_exact_notional():
    # Test when quantity * current_price is exactly equal to min_notional
    result = validate_quantity(5, 1, 100, 20, 100)
    assert result is None  # No exception should be raised


def test_validate_quantity_negative_quantity():
    # Test when quantity is negative (should raise an exception)
    with pytest.raises(ValueError, match="Quantity -5 is below the minimum allowed quantity of 1"):
        validate_quantity(-5, 1, 100, 20, 100)


def test_validate_quantity_zero_quantity():
    # Test when quantity is zero (should raise an exception)
    with pytest.raises(ValueError, match="Quantity 0 is below the minimum allowed quantity of 1"):
        validate_quantity(0, 1, 100, 20, 100)


def test_validate_quantity_invalid_current_price():
    # Test when current_price is zero (should raise an exception for notional check)
    with pytest.raises(ValueError, match="Total value 0 is below the minimum notional value of 100"):
        validate_quantity(5, 1, 100, 0, 100)


def test_validate_quantity_valid_quantity_with_large_notional():
    # Test when quantity is large but still valid for the minimum notional
    result = validate_quantity(100, 1, 1000, 2000, 1000)
    assert result is None  # No exception should be raised


def test_validate_quantity_invalid_max_qty():
    # Test with quantity equal to max_qty (valid, should not raise)
    result = validate_quantity(100, 1, 100, 20, 100)
    assert result is None  # No exception should be raised