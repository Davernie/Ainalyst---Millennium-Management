import json


def convert_code_to_json_string(file_path):
    try:
        with open(file_path, 'r') as file:
            code = file.read()

        # Convert the code into a JSON-compatible string (properly escaped)
        json_string = json.dumps({"code": code})
        return json_string

    except FileNotFoundError:
        return f"Error: The file {file_path} was not found."
    except Exception as e:
        return f"An error occurred: {str(e)}"


# Example usage:
file_path = '../../../fileForTesting.py'  # Replace with the actual file path
json_payload = convert_code_to_json_string(file_path)
print(json_payload)