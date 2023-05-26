import json
import os
import requests
import sys

headers = {
    "X-Auth-Email": os.environ["CF_API_EMAIL"],
    "X-Auth-Key": os.environ["CF_API_KEY"],
    "Content-Type": "application/json"
}

base_url = f"https://api.cloudflare.com/client/v4/accounts/{os.environ['CF_API_ACCOUNT_ID']}/gateway"

list_ids = []

for i in range(len(os.listdir())):
    if not os.path.isfile(f"list_{i+1}.txt"):
        break

    with open(f"list_{i+1}.txt", "r") as f:
        domains = f.read().split('\n')

    data = {
        "name": f"Blocked_Domains_List_{i+1}",
        "description": f"List of blocked domains (part {i+1})",
        "items": domains
    }

    response = requests.post(f"{base_url}/lists", headers=headers, data=json.dumps(data))
    list_id = response.json()["result"]["id"]
    list_ids.append(list_id)

expression = " or ".join([f"list('{list_id}')" for list_id in list_ids])
rule_data = {
    "action": "block",
    "expression": expression,
    "description": "Block all uploaded domain lists"
}

response = requests.post(f"{base_url}/rules", headers=headers, data=json.dumps(rule_data))
