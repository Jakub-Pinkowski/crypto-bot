from unittest.mock import patch

import pytest

from tests.order_execution.mock_data import MOCK_CONFIG_VALUES

# Mock `load_config_values`
with patch("utils.file_utils.load_config_values", return_value=MOCK_CONFIG_VALUES):
    from order_execution.executor_base import round_number


def test_round_quantity_to_step_size_exact_match():
    # Test where the quantity is already an exact multiple of step_size
    result = round_number(1.23, 0.01)
    assert result == 1.23


def test_round_quantity_to_step_size_round_down():
    # Test where the quantity rounds down to the nearest step size
    result = round_number(1.234, 0.01)
    assert result == 1.23


def test_round_quantity_to_step_size_round_up():
    # Test where the quantity rounds up to the nearest step size
    result = round_number(1.235, 0.01)
    assert result == 1.24


def test_round_quantity_to_step_size_no_decimal_places():
    # Test where step_size has no decimal places
    result = round_number(123, 5)
    assert result == 125


def test_round_quantity_to_step_size_large_step_size():
    # Test where step_size is larger than the quantity
    result = round_number(1.23, 2)
    assert result == 2


def test_round_quantity_to_step_size_small_step_size():
    # Test where step_size is very small
    result = round_number(1.23456789, 0.0001)
    assert result == 1.2346


def test_round_quantity_to_step_size_zero_quantity():
    # Test with quantity = 0
    result = round_number(0, 0.01)
    assert result == 0


def test_round_quantity_to_step_size_zero_step_size():
    # Test with step_size = 0 (should raise an exception)
    with pytest.raises(ZeroDivisionError):
        round_number(1.23, 0)


def test_round_quantity_to_step_size_invalid_step_size():
    # Test with invalid step_size (non-numeric value)
    with pytest.raises(TypeError):
        round_number(1.23, "invalid")


def test_round_quantity_to_step_size_invalid_quantity():
    # Test with invalid quantity (non-numeric value)
    with pytest.raises(TypeError):
        round_number("invalid", 0.01)


def test_round_quantity_to_step_size_negative_quantity():
    # Test with negative quantity
    result = round_number(-1.23, 0.01)
    assert result == -1.23


def test_round_quantity_to_step_size_negative_step_size():
    # Test with negative step_size
    with pytest.raises(ValueError, match="Step size must be greater than or equal to 0."):
        round_number(1.23, -0.01)
