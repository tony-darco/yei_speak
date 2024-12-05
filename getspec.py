import requests
import json

url = "https://api.meraki.com/api/v1/organizations/1628211/openapiSpec"

headers = {
    "X-Cisco-Meraki-API-KEY": "363d7285c92d1cf87c7cc924d5bdb71fb90c2cd8",
    "Content-Type": "application/json"
}

params = {
    "version": 3
}

response = requests.get(url, headers=headers, params=params).json()

# Open a file to write the output
with open("endpoint_description.txt", "w") as file:
    # Check if 'paths' is in the response
    if 'paths' in response:
        paths = response['paths']
        # Iterate through the paths and write each path and description to the file
        for path, methods in paths.items():
            file.write(f"Path: {path}\n")
            for method, details in methods.items():
                # Look for description in the details
                description = details.get('description', 'No description available.')
                file.write(f"  Method: {method.upper()}\n")
                file.write(f"  Description: {description}\n")
            file.write("-" * 40 + "\n")  # Separator for clarity
    else:
        file.write("No paths found in the API response.\n")

print("Descriptions saved to 'endpoint_description.txt'")
