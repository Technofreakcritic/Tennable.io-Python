import requests
import os
from datetime import datetime, timedelta

THRESHOLD_DAYS = 7

def get_threshold_time(days):
    current_time = datetime.utcnow()
    return current_time - timedelta(days=days)

def get_list_of_dead_assets(json_data, threshold_time):
    count_old_instances = 0
    old_instance_ids = []

    for asset in json_data.get("assets", []):
        last_seen_value = asset.get("last_seen")
        if last_seen_value:
            last_seen_time = datetime.strptime(last_seen_value, "%Y-%m-%dT%H:%M:%S.%fZ")
            if last_seen_time < threshold_time:
                count_old_instances += 1
                old_instance_ids.append(asset.get("id"))
                print(asset.get("id"))

    return old_instance_ids

def delete_assets(headers, host_ids):
    delete_job_url = "https://cloud.tenable.com/api/v2/assets/bulk-jobs/delete"

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

def get_host_details(headers, hosts, threshold_time):
    matching_hosts = []

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
                    matching_hosts.append(host_data.get("id"))
                    print(host_data.get("id"))
        else:
            print(f"Failed to retrieve details for host: {host}")
            print(f"Status code: {response.status_code}")

    return matching_hosts

url = "https://cloud.tenable.com/assets"

main_headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "X-ApiKeys": os.getenv('TENABLE_API_KEY')
}

try:
    response = requests.get(url, headers=main_headers)
    response.raise_for_status()

except requests.exceptions.RequestException as e:
    print("Error making the API request:", e)
    response = None

if response is not None:
    threshold_time = get_threshold_time(THRESHOLD_DAYS)

    host_ids = get_list_of_dead_assets(response.json(), threshold_time)
    print("------BREAK-----")
    license_check = get_host_details(main_headers, host_ids, threshold_time)
    print("---KILL STREAK----")
    delete_assets(main_headers, license_check)

else:
    print("API request failed. Cannot proceed.")
