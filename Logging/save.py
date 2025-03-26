# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 11:54:11 2024

@author: Johannes Eberle
@functionality: Store data and save information about it
"""

import os
import json
import h5py
import numpy as np
from datetime import datetime

def serialize_data_for_json(data):
    """
    Convert data dictionary into a JSON-serializable format.

    Args:
        data (dict): A dictionary with potentially non-JSON-serializable values.

    Returns:
        dict: A JSON-serializable dictionary.
    """
    def custom_serializer(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()  # Convert ndarray to list
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    # Recursively serialize the data
    return json.loads(json.dumps(data, default=custom_serializer))

def save_measurement(data, descriptions, base_folder="Z:\\Projects\\Defects for QTM\\Raw_data_zerui\\"):
    """
    Save measurement data and descriptions in an HDF5 file with a timestamped filename in a date-based folder
    and update a timestamped summary JSON file.

    Args:
        data (dict): A dictionary containing measurement data.
        descriptions (dict): A dictionary containing descriptions of the measurement.
        base_folder (str): The base folder to store measurements, organized by date.
    """
    # Get the current date and timestamp for organization
    date_str = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    # Define the date folder path
    date_folder = os.path.join(base_folder, date_str)
    os.makedirs(date_folder, exist_ok=True)

    # Define filename prefix from descriptions entry
    measurement_name = descriptions.get("measurement", "measurement")

    # Determine the measurement index
    measurement_files = os.listdir(date_folder)
    existing_indices = [
        int(file.split("_")[0]) for file in measurement_files if file.split("_")[0].isdigit()
    ]
    next_index = max(existing_indices, default=0) + 1

    # Define indexed file names
    hdf5_file_path = os.path.join(date_folder, f"{next_index}_{measurement_name}_{timestamp}.h5")
    summary_file_path = os.path.join(date_folder, f"{next_index}_summary_{timestamp}.json")

    # Save measurement data in HDF5
    with h5py.File(hdf5_file_path, "a") as hdf5_file:
        # Create a group for this measurement
        group_index = len(hdf5_file.keys()) + 1
        group = hdf5_file.create_group(f"measurement_{group_index}")

        # Add timestamp to descriptions for record-keeping
        descriptions['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Save measurement data
        data_group = group.create_group("data")
        for key, value in data.items():
            try:
                # Save lists, tuples, and arrays as datasets
                if isinstance(value, (list, tuple, np.ndarray)):
                    data_group.create_dataset(key, data=value)
                # Save simple values as attributes
                elif isinstance(value, (str, int, float, bool)):
                    data_group.attrs[key] = value
                # Save dictionaries or other complex data as JSON strings in datasets
                else:
                    data_group.create_dataset(key, data=json.dumps(value))
            except Exception as e:
                print(f"Error saving {key}: {e}")

        # Save descriptions
        desc_group = group.create_group("descriptions")
        for key, value in descriptions.items():
            try:
                # Save simple values as attributes
                if isinstance(value, (str, int, float, bool)):
                    desc_group.attrs[key] = value
                # Save lists, tuples, and arrays as datasets
                elif isinstance(value, (list, tuple, np.ndarray)):
                    desc_group.create_dataset(key, data=value)
                # Save dictionaries or other complex data as JSON strings in datasets
                else:
                    desc_group.create_dataset(key, data=json.dumps(value))
            except Exception as e:
                print(f"Error saving description {key}: {e}")

        # Add general metadata about the dataset
        group.attrs['description'] = "Measurement data and descriptions with timestamped metadata"
        group.attrs['created_on'] = date_str

    # Update the summary JSON file with measurement metadata
    summary_entry = {
        "measurement": f"measurement_{group_index}",
        **serialize_data_for_json(descriptions)
    }

    # If the JSON file already exists, load existing data and append
    if os.path.exists(summary_file_path):
        with open(summary_file_path, "r") as summary_file:
            summary_data = json.load(summary_file)
        summary_data.append(summary_entry)
    else:
        # Start a new summary list
        summary_data = [summary_entry]

    # Save the updated summary data to the JSON file
    with open(summary_file_path, "w") as summary_file:
        json.dump(summary_data, summary_file, indent=4)

    print(f"Data saved successfully to {hdf5_file_path}")
    print(f"Summary saved to {summary_file_path}")

def load_data(hdf5_file_path, include_descriptions=False):
    """
    Load measurement data and optionally descriptions from an HDF5 file.

    Args:
        hdf5_file_path (str): Path to the HDF5 file.
        include_descriptions (bool): Whether to include descriptions in the returned data.

    Returns:
        dict: A dictionary containing the measurement data and optionally descriptions.
    """
    data = {"data": {}, "descriptions": {}}
    with h5py.File(hdf5_file_path, "r") as hdf5_file:
        for measurement_key in hdf5_file.keys():
            measurement_group = hdf5_file[measurement_key]

            # Load data group
            if "data" in measurement_group:
                data_group = measurement_group["data"]
                for key, value in data_group.items():
                    data["data"][key] = value[()] if isinstance(value, h5py.Dataset) else value.attrs[key]

            # Load descriptions group if requested
            if include_descriptions and "descriptions" in measurement_group:
                desc_group = measurement_group["descriptions"]
                for key in desc_group.attrs:
                    data["descriptions"][key] = desc_group.attrs[key]
                for key, value in desc_group.items():
                    data["descriptions"][key] = value[()] if isinstance(value, h5py.Dataset) else value.attrs[key]

    if not include_descriptions:
        return data["data"]
    return data

def sync_hdf5_with_json(date, file_index, base_folder="Z:\\Projects\\Defects for QTM\\Raw_data_zerui\\"):
    """
    Sync the updated parameters from the JSON file to the corresponding HDF5 file.

    Args:
        base_folder (str): Base folder where the data is stored, organized by date.
        date (str): Date of the measurement folder (e.g., "2024-10-31").
        file_index (int): Index of the measurement file to be updated.
    """
    date_folder = os.path.join(base_folder, date)
    hdf5_file_path = None
    json_file_path = None

    for file_name in os.listdir(date_folder):
        if file_name.startswith(f"{file_index}_") and file_name.endswith(".h5"):
            hdf5_file_path = os.path.join(date_folder, file_name)
        if file_name.startswith(f"{file_index}_") and file_name.endswith(".json"):
            json_file_path = os.path.join(date_folder, file_name)

    if not hdf5_file_path or not json_file_path:
        print("Error: Corresponding HDF5 or JSON file not found.")
        return

    # Debug: Print the JSON file content
    with open(json_file_path, 'r') as summary_file:
        json_content = summary_file.read()
        print("JSON Content:", json_content)  # Print JSON content to check for errors
        try:
            summary_data = json.loads(json_content)
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            return
