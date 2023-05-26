import os
import requests

url = "https://raw.githubusercontent.com/MartinatorTime/Cloudflare-adblock-py/main/cloudflare/lists/hosts.txt"
response = requests.get(url)
domains = response.text.split('\n')

chunk_size = 1000
chunks = [domains[i:i + chunk_size] for i in range(0, len(domains), chunk_size)]

headers = {
    "X-Auth-Key": os.environ["CF_API_KEY"],
    "X-Auth-Email": os.environ["CF_API_EMAIL"],
    "Content-Type": "application/json",
}

list_ids = []

for i, chunk in enumerate(chunks):
    data = {
        "name": f"adblock_list_{i + 1}",
        "description": f"Adblock list {i + 1}",
        "items": chunk,
    }
    response = requests.post(f"https://api.cloudflare.com/client/v4/accounts/{os.environ['CF_API_ACCOUNT_ID']}/gateway/lists", json=data, headers=headers)
    response.raise_for_status()
    list_id = response.json()["result"]["id"]
    list_ids.append(list_id)

rule_expression = " or ".join([f'dns.list("list-{list_id}")' for list_id in list_ids])

rule_data = {
    "expression": rule_expression,
    "action": "block",
    "enabled": True,
}

response = requests.post(f"https://api.cloudflare.com/client/v4/accounts/{os.environ['CF_API_ACCOUNT_ID']}/gateway/rules", json=rule_data, headers=headers)
response.raise_for_status()
