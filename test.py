import json

# Function to read the JSON file and return the data as a list
def read_json_file(file_path):
    try:
        # Open and load the JSON data from the file
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"The file at {file_path} was not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the file at {file_path}.")
        return []

# Example usage
if __name__ == "__main__":
    # Specify the path to your JSON file
    file_path = 'endpoint_description.json'  # Update with your file path
    json_data = read_json_file(file_path)
    
    # Print the resulting list
    if json_data:
        print("JSON Data as List:")
        print(json_data)
    else:
        print("No data or error occurred.")
