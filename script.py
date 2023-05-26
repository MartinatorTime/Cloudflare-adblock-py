import os
import json
import requests

def split_domains(filename):
    with open(filename) as f:
        domains = f.read().splitlines()

    chunk_size = 1000
    for i in range(0, len(domains), chunk_size):
        with open(f"list{i // chunk_size + 1}.txt", "w") as f:
            f.write("\n".join(domains[i:i + chunk_size]))

    return (i // chunk_size) + 1

def upload_domain_list(list_name, filename):
    url = f"https://api.cloudflare.com/client/v4/accounts/{os.environ['CF_API_ACCOUNT_ID']}/gateway/lists"
    headers = {
        "X-Auth-Email": os.environ["CF_API_EMAIL"],
        "X-Auth-Key": os.environ["CF_API_KEY"],
        "Content-Type": "application/json"
    }
    data = {
        "name": list_name,
        "description": f"Blocked domains {list_name}",
        "kind": "ip",
        "file": filename
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()["result"]["id"]

def create_firewall_rule(list_ids):
    url = f"https://api.cloudflare.com/client/v4/accounts/{os.environ['CF_API_ACCOUNT_ID']}/gateway/rules"
    headers = {
        "X-Auth-Email": os.environ["CF_API_EMAIL"],
        "X-Auth-Key": os.environ["CF_API_KEY"],
        "Content-Type": "application/json"
    }
    expression = " | ".join([f'domain in list("{list_id}")' for list_id in list_ids])
    data = {
        "action": "block",
        "expression": expression,
        "description": "Block domains from uploaded lists"
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()["result"]["id"]

def main():
    num_files = split_domains("blocked_domains.txt")
    list_ids = []

    for i in range(1, num_files + 1):
        list_id = upload_domain_list(f"list{i}", f"list{i}.txt")
        list_ids.append(list_id)

    rule_id = create_firewall_rule(list_ids)
    print(f"Firewall rule created with ID: {rule_id}")

if __name__ == "__main__":
    main()
