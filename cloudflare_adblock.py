import os
import requests
import json

# Constants
url = "https://raw.githubusercontent.com/MartinatorTime/Cloudflare-adblock-py/main/cloudflare/lists/hosts.txt"
upload_url = "https://api.cloudflare.com/client/v4/accounts/{identifier}/gateway/lists"
dns_rules_url = "https://api.cloudflare.com/client/v4/accounts/{identifier}/gateway/rules"

# Github secrets
cf_api_key = os.getenv("CF_API_KEY")
cf_api_account_id = os.getenv("CF_API_ACCOUNT_ID")
cf_api_email = os.getenv("CF_API_EMAIL")

# Headers
headers = {
    "X-Auth-Key": cf_api_key,
    "X-Auth-Email": cf_api_email,
    "Content-Type": "application/json"
}

def download_blocked_domains():
    response = requests.get(url)
    if response.status_code == 200:
        return response.text.splitlines()
    else:
        raise Exception(f"Error downloading blocked domains: {response.status_code}")

def split_domains(domains, chunk_size=1000):
    return [domains[i:i + chunk_size] for i in range(0, len(domains), chunk_size)]

def upload_domain_lists(lists):
    list_ids = []
    for idx, domain_list in enumerate(lists):
        data = {
            "name": f"Blocked Domains List {idx + 1}",
            "items": domain_list
        }
        response = requests.post(upload_url.format(identifier=cf_api_account_id), headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            list_ids.append(response.json()["result"]["id"])
        else:
            raise Exception(f"Error uploading domain list {idx + 1}: {response.status_code}")
    return list_ids

def create_dns_policy(list_ids):
    expressions = [f"list_id({list_id})" for list_id in list_ids]
    expression = " or ".join(expressions)

    data = {
        "name": "Blocked Domains Policy",
        "expression": expression,
        "action": "block"
    }
    response = requests.post(dns_rules_url.format(identifier=cf_api_account_id), headers=headers, data=json.dumps(data))
    if response.status_code != 200:
        raise Exception(f"Error creating DNS policy: {response.status_code}")

def main():
    domains = download_blocked_domains()
    lists = split_domains(domains)
    list_ids = upload_domain_lists(lists)
    create_dns_policy(list_ids)

if __name__ == "__main__":
    main()
