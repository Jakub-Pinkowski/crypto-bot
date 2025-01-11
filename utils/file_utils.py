import json
import yaml
import os
from datetime import datetime

def save_data_to_file(data, file_path, file_name):

    # Define timestamps, filename and folder name
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{file_name}_{timestamp}.json"
    date_folder = datetime.now().strftime("%Y-%m-%d")

    # Prepare the directory
    base_dir = os.path.dirname(os.path.dirname(__file__))
    directory = os.path.join(base_dir, "data", file_path, date_folder)
    os.makedirs(directory, exist_ok=True)

    # Save the data as JSON
    file_path = os.path.join(directory, filename)
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

def load_config_values(*keys):
    config_path = os.path.join("config", "config.yaml")  # Relative file path

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found at '{config_path}'")

    with open(config_path, "r") as file:
        try:
            config = yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error while parsing the config file: {str(e)}")

    # Extract the requested keys
    requested_values = {}
    for key in keys:
        if key not in config:
            raise KeyError(f"Key '{key}' is missing in the config file")
        requested_values[key] = config[key]

    return requested_values
