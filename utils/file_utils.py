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

def load_data_from_file(file_path, file_name):
    # NOTE: Loads the latest file by default
    # Prepare the directory
    base_dir = os.path.dirname(os.path.dirname(__file__))
    directory = os.path.join(base_dir, "data", file_path)

    # Get the most recent date folder
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory not found: {directory}")

    date_folders = sorted(
        [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))],
        reverse=True
    )
    if not date_folders:
        raise FileNotFoundError(f"No date folders found in: {directory}")

    latest_date_folder = os.path.join(directory, date_folders[0])

    # Find the latest file with the specified prefix
    matching_files = sorted(
        [f for f in os.listdir(latest_date_folder) if f.startswith(file_name) and f.endswith(".json")],
        reverse=True
    )
    if not matching_files:
        raise FileNotFoundError(f"No files found with prefix '{file_name}' in folder: {latest_date_folder}")

    latest_file = os.path.join(latest_date_folder, matching_files[0])

    # Read and return the JSON data
    with open(latest_file, "r") as file:
        data = json.load(file)

    return data

def load_config_values(*keys):
    config_path = os.path.join("config", "config.yaml")

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
