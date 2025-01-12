import pytest
from unittest.mock import patch, mock_open, MagicMock
import os
import json
import yaml
from utils.file_utils import save_data_to_file, load_config_values


def test_save_data_to_file_creates_directory():
    test_data = {"key": "value"}
    test_file_path = "test_path"
    test_file_name = "test_file"

    with patch("os.makedirs") as mock_makedirs, patch("builtins.open", mock_open()), patch(
            "utils.file_utils.datetime") as mock_datetime:
        # Mock datetime to return consistent timestamp
        mock_now = MagicMock()
        mock_now.strftime.return_value = "2023-10-31"
        mock_datetime.now.return_value = mock_now  # Return mocked datetime when now() is called

        save_data_to_file(test_data, test_file_path, test_file_name)

        # Adjust base_dir to go one level up from test directory
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # Go one more level up
        expected_path = os.path.join(base_dir, "data", test_file_path, "2023-10-31")

        mock_makedirs.assert_called_once_with(expected_path, exist_ok=True)

def test_save_data_to_file_creates_correct_file():
    test_data = {"key": "value"}
    test_file_path = "test_path"
    test_file_name = "test_file"

    with patch("os.makedirs") as mock_makedirs, patch("builtins.open", mock_open()) as mock_file, patch(
            "utils.file_utils.datetime") as mock_datetime:
        # Mock datetime to return consistent timestamp
        mock_now = MagicMock()
        mock_now.strftime.return_value = "2023-10-31"
        mock_now.strftime.side_effect = lambda fmt: fmt.replace("%Y", "2023").replace("%m", "10").replace("%d", "31") \
            .replace("%H", "12").replace("%M", "30").replace("%S", "00")
        mock_datetime.now.return_value = mock_now  # Return mocked datetime when now() is called

        save_data_to_file(test_data, test_file_path, test_file_name)

        # Adjust base_dir to go one level up from test directory
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # Go one more level up
        expected_dir = os.path.join(base_dir, "data", test_file_path, "2023-10-31")
        expected_file_path = os.path.join(expected_dir, f"{test_file_name}_2023-10-31_12-30-00.json")

        # Assert `os.makedirs` was called to create the directory
        mock_makedirs.assert_called_once_with(expected_dir, exist_ok=True)

        # Assert the file was created correctly
        mock_file.assert_called_once_with(expected_file_path, "w")

        # Assert the file content is written correctly
        mock_file_handle = mock_file()

        # Collect all calls to write and join them
        written_content = "".join(call.args[0] for call in mock_file_handle.write.call_args_list)
        assert written_content == json.dumps(test_data, indent=4)

def test_load_config_values_success():
    config = {
        "key1": "value1",
        "key2": "value2",
    }

    # Mock the file existence and content
    with patch("builtins.open", mock_open(read_data=yaml.dump(config))) as mock_file, \
            patch("os.path.exists", return_value=True):
        # Call the function with keys
        result = load_config_values("key1", "key2")

        # Verify the result matches our mock data
        assert result == {"key1": "value1", "key2": "value2"}
        mock_file.assert_called_once_with(os.path.join("config", "config.yaml"), "r")

def test_load_config_values_file_not_found():
    # Mock the config file does not exist
    with patch("os.path.exists", return_value=False):
        with pytest.raises(FileNotFoundError, match="Config file not found at 'config/config.yaml'"):
            load_config_values("key1")

def test_load_config_values_parse_error():
    # Mock a malformed YAML file
    with patch("builtins.open", mock_open(read_data="key1: value1:")), \
            patch("os.path.exists", return_value=True):
        with pytest.raises(yaml.YAMLError, match="Error while parsing the config file:"):
            load_config_values("key1")

def test_load_config_values_missing_key():
    config = {
        "key1": "value1",
    }

    # Mock the file existence and content
    with patch("builtins.open", mock_open(read_data=yaml.dump(config))), \
            patch("os.path.exists", return_value=True):
        with pytest.raises(KeyError, match="Key 'key2' is missing in the config file"):
            load_config_values("key1", "key2")