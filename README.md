# Tenable.io Asset Cleanup Script Python

This script retrieves a list of assets from the Tenable API and deletes assets that have not been seen in the last 5 days.

## Prerequisites

Before using this script, make sure you have the following:

- Tenable API Key: You will need an API key from Tenable to access the Tenable API.

## Usage

1. Clone this repository to your local machine.

2. Set your Tenable API key as an environment variable:

   ```shell
   export TENABLE_API_KEY=your_api_key_here

3. Run the script using Python:
   python3 main.py


# Process Flow

    The script sends an HTTP GET request to the Tenable API to retrieve a list of assets.

    It parses the JSON response and filters for assets that have not been seen in the last 5 days.

    The script prints the count of assets older than 5 days and their host IDs.

    It then sends DELETE requests to the Tenable API to delete these assets.

# Error Handling

The script includes error handling to handle potential issues when making API requests and deleting assets.
Dependencies

    Python 3.x
    Requests library for making HTTP requests (install using pip install requests)

# Author

CoffeeBoii

# License

This project is licensed under the MIT License - see the LICENSE.md file for details.