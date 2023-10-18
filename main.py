import requests
import json
from datetime import datetime, timedelta
import os

#  Process Flow
# 1. Get response from API server
# 2. Since the response is in string convert it into readable json
# 3. Filter for valuable infoormation
# 4. Print the list of dead assets based on the filter
# 5. Print the count of dead assets based on the filter

url = "https://cloud.tenable.com/assets"

main_headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "X-ApiKeys": os.getenv('TENABLE_API_KEY')
    }

try:
    response = requests.get(url, headers=main_headers)
    response.raise_for_status()  # Raise an exception for HTTP errors

except requests.exceptions.RequestException as e:
    print("Error making the API request:", e)
    response = None  # Set response to None in case of an error



def get_list_of_dead_assets(response):

    # Load the response text into a variable
    json_data = response.text

    # Parse the data into a dict 
    json_data = json.loads(json_data)

    # Just a placeholder to check if the json works
    # print(json.dumps(json_data, sort_keys=True, indent=2))

    # # Define the current time
    current_time = datetime.utcnow()

    # # Calculate the threshold time (2 days ago)
    threshold_time = current_time - timedelta(days=7)

    # # Initialize a count for instances more than 2 days old
    count_old_instances = 0

    # Initialize a list to store the host IDs of instances more than 2 days old
    old_instance_ids = []

    # # Iterate through instances to count those more than 2 days old
    for asset in json_data.get("assets", []):
        last_seen_value = asset.get("last_seen")
        if last_seen_value:
            last_seen_time = datetime.strptime(last_seen_value, "%Y-%m-%dT%H:%M:%S.%fZ")
            if last_seen_time < threshold_time:
                count_old_instances += 1
                old_instance_ids.append(asset.get("id"))


    # Print the count of instances more than 2 days old --- This works
    print(f"Count of instances more than 2 days old: {count_old_instances}")
    print(old_instance_ids)
    return old_instance_ids


# Let's goooooo MY API fucntion works
# Time to create try catch error statements for this function
# And connection between these 2 functions



def delete_assets(headers, host_ids):
    delete_job_url = "https://cloud.tenable.com/api/v2/assets/bulk-jobs/delete"

    # Iterate through host_ids and send a DELETE request for each one
    for host_id in host_ids:
        payload = {
            "query": {
                "field": "host.id",
                "operator": "eq",
                "value": host_id
            },
            "hard_delete": False
        }

        try:
            response = requests.post(delete_job_url, json=payload, headers=headers)
            response.raise_for_status()
            print(f"Deleted asset with host_id: {host_id}")

        except requests.exceptions.RequestException as e:
            print(f"Error deleting asset with host_id {host_id}: {e}")


def get_host_details(headers, hosts):
    current_time = datetime.utcnow()
    threshold_time = current_time - timedelta(days=7)
    
    matching_hosts = []  # Initialize an empty list to store matching hosts
    
    for host in hosts:
        url = f"https://cloud.tenable.com/assets/{host}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            host_data = response.json()
            last_licensed_scan_date = host_data.get("last_licensed_scan_date")
            last_seen = host_data.get("last_seen")

            if last_licensed_scan_date is None and last_seen:
                last_seen_time = datetime.strptime(last_seen, "%Y-%m-%dT%H:%M:%S.%fZ")
                
                if last_seen_time < threshold_time:
                    matching_hosts.append(host_data.get("id"))  # Append the host data to the list
                    # print(host_data)
        else:
            print(f"Failed to retrieve details for host: {host}")
            print(f"Status code: {response.status_code}")
    
    return matching_hosts  # Return the list of matching hosts


# Continue with the rest of the code, checking if response is not None before using it
if response is not None:
    # Call the function with the response
    host_ids = get_list_of_dead_assets(response)
    license_check = get_host_details(main_headers, host_ids)
    delete_assets(main_headers, license_check)
else:
    print("API request failed. Cannot proceed.")






