import json
import os

def load_json_file(file_path):
    """Loads a JSON file and returns the dictionary."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return None

def format_log_for_prompt(log_data):
    """Converts a log dictionary into a string suitable for LLM prompting."""
    return json.dumps(log_data, indent=2)
