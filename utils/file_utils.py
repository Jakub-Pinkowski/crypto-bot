import json
import os
from datetime import datetime


def save_data_to_file(data, file_path, file_name):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{file_name}_{timestamp}.json"
    date_folder = datetime.now().strftime("%Y-%m-%d")

    base_dir = os.path.dirname(os.path.dirname(__file__))  # Navigate to project root
    directory = os.path.join(base_dir, "data", file_path, date_folder)
    os.makedirs(directory, exist_ok=True)  # Ensure target directory exists

    # Save the data as JSON
    file_path = os.path.join(directory, filename)  # Prepare file path with new structure
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
