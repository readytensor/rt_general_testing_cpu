import json
import os
import random
import time
import tracemalloc
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Union


def list_image_files(directory):
    """
    Returns a list of all image files in the given directory, including files in
    subdirectories.

    :param directory: The path to the directory to scan for image files.
    :return: A list of paths to the image files in the directory.
    """
    image_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".tiff",
        ".webp",
    }  # Add or remove extensions as needed
    image_files_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if os.path.splitext(file)[1].lower() in image_extensions:
                image_files_list.append(os.path.join(root, file))
    return image_files_list


def read_json_as_dict(input_path: str) -> Dict:
    """
    Reads a JSON file and returns its content as a dictionary.
    If input_path is a directory, the first JSON file in the directory is read.
    If input_path is a file, the file is read.

    Args:
        input_path (str): The path to the JSON file or directory containing a JSON file.

    Returns:
        dict: The content of the JSON file as a dictionary.

    Raises:
        ValueError: If the input_path is neither a file nor a directory,
                    or if input_path is a directory without any JSON files.
    """
    if os.path.isdir(input_path):
        # Get all the JSON files in the directory
        json_files = [
            os.path.join(input_path, f)
            for f in os.listdir(input_path)
            if f.endswith(".json")
        ]

        # If there are no JSON files, raise a ValueError
        if not json_files:
            raise ValueError("No JSON files found in the directory")

        # Else, get the path of the first JSON file
        json_file_path = json_files[0]

    elif os.path.isfile(input_path):
        json_file_path = input_path
    else:
        raise ValueError("Input path is neither a file nor a directory")

    # Read the JSON file and return it as a dictionary
    with open(json_file_path, "r", encoding="utf-8") as file:
        json_data_as_dict = json.load(file)

    return json_data_as_dict


def read_csv_in_directory(file_dir_path: str) -> pd.DataFrame:
    """
    Reads a CSV file in the given directory path as a pandas dataframe and returns
    the dataframe.

    Args:
    - file_dir_path (str): The path to the directory containing the CSV file.

    Returns:
    - pd.DataFrame: The pandas dataframe containing the data from the CSV file.

    Raises:
    - FileNotFoundError: If the directory does not exist.
    - ValueError: If no CSV file is found in the directory or if multiple CSV files are
        found in the directory.
    """
    if not os.path.exists(file_dir_path):
        raise FileNotFoundError(f"Directory does not exist: {file_dir_path}")

    csv_files = [file for file in os.listdir(file_dir_path) if file.endswith(".csv")]

    if not csv_files:
        raise ValueError(f"No CSV file found in directory {file_dir_path}")

    if len(csv_files) > 1:
        raise ValueError(f"Multiple CSV files found in directory {file_dir_path}.")

    csv_file_path = os.path.join(file_dir_path, csv_files[0])
    df = pd.read_csv(csv_file_path)
    return df


def set_seeds(seed_value: int) -> None:
    """
    Set the random seeds for Python, NumPy, etc. to ensure
    reproducibility of results.

    Args:
        seed_value (int): The seed value to use for random
            number generation. Must be an integer.

    Returns:
        None
    """
    if isinstance(seed_value, int):
        os.environ["PYTHONHASHSEED"] = str(seed_value)
        random.seed(seed_value)
        np.random.seed(seed_value)
    else:
        raise ValueError(f"Invalid seed value: {seed_value}. Cannot set seeds.")


def save_dataframe_as_csv(dataframe: pd.DataFrame, file_path: str) -> None:
    """
    Saves a pandas dataframe to a CSV file in the given directory path.
    Float values are saved with 4 decimal places.

    Args:
    - df (pd.DataFrame): The pandas dataframe to be saved.
    - file_path (str): File path and name to save the CSV file.

    Returns:
    - None

    Raises:
    - IOError: If an error occurs while saving the CSV file.
    """
    try:
        dataframe.to_csv(file_path, index=False, float_format="%.8f")
    except IOError as exc:
        raise IOError(f"Error saving CSV file: {exc}") from exc


def clear_files_in_directory(directory_path: str) -> None:
    """
    Clears all files in the given directory path.

    Args:
    - directory_path (str): The path to the directory containing the files
        to be cleared.

    Returns:
    - None
    """
    for file in os.listdir(directory_path):
        file_path = os.path.join(directory_path, file)
        os.remove(file_path)


def save_json(file_path_and_name: str, data: Any) -> None:
    """Save json to a path (directory + filename)"""
    with open(file_path_and_name, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            default=lambda o: make_serializable(o),
            sort_keys=True,
            indent=4,
            separators=(",", ": "),
        )


def make_serializable(obj: Any) -> Union[int, float, List[Union[int, float]], Any]:
    """
    Converts a given object into a serializable format.

    Args:
    - obj: Any Python object

    Returns:
    - If obj is an integer or numpy integer, returns the integer value as an int
    - If obj is a numpy floating-point number, returns the floating-point value
        as a float
    - If obj is a numpy array, returns the array as a list
    - Otherwise, uses the default behavior of the json.JSONEncoder to serialize obj

    """
    if isinstance(obj, (int, np.integer)):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return json.JSONEncoder.default(None, obj)


def contains_subdirectories(directory):
    """Check if the specified directory contains any subdirectories."""
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            return True
    return False


class ResourceTracker(object):
    """
    This class serves as a context manager to track time and
    memory allocated by code executed inside it.
    """

    def __init__(self, logger):
        self.logger = logger

    def __enter__(self):
        self.start_time = time.time()
        tracemalloc.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end_time = time.time()
        _, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        elapsed_time = self.end_time - self.start_time

        self.logger.info(f"CPU Memory allocated (peak): {peak_memory / 10**6:.2f}MB")
        self.logger.info(f"Execution time: {elapsed_time:.2f} seconds")
        self.logger.info(f"Host CPU count: {os.cpu_count()}")
        self.logger.info(f"Container CPU count: {len(os.sched_getaffinity(0))}")
