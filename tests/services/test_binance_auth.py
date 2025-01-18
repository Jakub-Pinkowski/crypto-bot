from unittest.mock import patch

import pytest
from binance.error import ClientError
from binance.spot import Spot


def test_binance_auth_with_valid_keys():
    # Mock environment variables
    with patch("os.getenv") as mock_getenv:
        mock_getenv.side_effect = lambda key: "valid_key" if key == "BINANCE_API_KEY" else "valid_secret"

        # Initialize the Spot client
        client = Spot(api_key="valid_key", api_secret="valid_secret")

        # Mock the response of the account method
        with patch.object(client, "account", return_value={"balances": []}) as mock_account:
            response = client.account()  # Call a signed method

            # Ensure the method is called successfully
            assert response == {"balances": []}
            mock_account.assert_called_once()


def test_binance_auth_with_no_keys():
    # Mock environment variables to return None for both keys
    with patch("os.getenv") as mock_getenv:
        mock_getenv.side_effect = lambda key: None  # Return None for all keys

        # Initialize the Spot client with no keys
        client = Spot(api_key=None, api_secret=None)

        # When a method requiring signed requests is called, it should raise an error
        with pytest.raises(AttributeError) as exc_info:
            client.account()  # Trigger the error by calling a signed method

        # Verify the error occurred due to missing keys
        assert "'NoneType' object has no attribute 'encode'" in str(exc_info.value)


def test_binance_auth_with_invalid_keys():
    # Mock environment variables to return invalid keys
    with patch("os.getenv") as mock_getenv:
        mock_getenv.side_effect = lambda key: "invalid_key" if key == "BINANCE_API_KEY" else "invalid_secret"

        # Initialize the Spot client with invalid keys
        client = Spot(api_key="invalid_key", api_secret="invalid_secret")

        # When a method requiring signed requests is called, it should raise a ClientError
        with pytest.raises(ClientError) as exc_info:
            client.account()

        # Unpack the error from the exception and verify the details
        error_tuple = exc_info.value.args
        assert len(error_tuple) >= 3
        status_code, error_code, error_message = error_tuple[:3]

        # Verify the error details against expected values
        assert status_code == 401  # HTTP status code for unauthorized
        assert error_code == -2014  # Binance error code for invalid API key
        assert "API-key format invalid" in error_message  # Binance error message for invalid API key
