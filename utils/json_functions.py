import json
import re

def clean_json_string(json_data: str) -> str:
    """Clean and format JSON strings returned by the AI, and fix truncation issues.

    This function:
      1. Removes markdown code block markers and an optional language identifier (e.g., "json").
      2. Uses a bracket balancing algorithm to truncate the output at the last balanced closing bracket.
      3. Ensures that if the JSON starts with '[' it ends with ']', or if it starts with '{' it ends with '}'.
    """
    # Remove markdown code block markers and optional language specifier.
    json_data = re.sub(r'^```(?:json)?\s*', '', json_data, flags=re.IGNORECASE)
    json_data = re.sub(r'\s*```$', '', json_data)
    json_data = json_data.strip()

    if not json_data:
        return json_data

    # Determine if we're dealing with a JSON array or object.
    first_char = json_data[0]
    if first_char == '[':
        open_char, close_char = '[', ']'
    elif first_char == '{':
        open_char, close_char = '{', '}'
    else:
        return json_data  # Not a valid JSON object/array.

    # Use a counter to track the balance of the brackets.
    count = 0
    last_complete_index = None
    for i, ch in enumerate(json_data):
        if ch == open_char:
            count += 1
        elif ch == close_char:
            count -= 1
            if count == 0:
                last_complete_index = i
    # If a balanced closing bracket is found, truncate the string there.
    if last_complete_index is not None:
        json_data = json_data[:last_complete_index + 1]

    # Ensure that the JSON ends with the proper closing bracket.
    if first_char == '[' and not json_data.endswith(']'):
        json_data += ']'
    elif first_char == '{' and not json_data.endswith('}'):
        json_data += '}'

    return json_data.strip()


def download_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {file_path}")
        return None
