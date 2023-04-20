import os
import CloudFlare
import datetime
import requests
from CloudFlare.exceptions import CloudFlareAPIError
from requests import HTTPError

try:
  token = os.environ['CF_API_TOKEN']
  email = os.environ['CF_API_EMAIL']
  account_id = os.environ['CF_API_ACCOUNT_ID']
except KeyError:
  print(
    'CF_API_TOKEN, CF_API_EMAIL, or CF_API_ACCOUNT_ID environment variable not set'
  )


def get_block_list(block_list_url):
  block_list = requests.get(
    block_list_url).text.splitlines()[:300000]  # limit list to 300000 domains
  return block_list


def blockListToMaxSize(block_list):
  res = []
  for i in range(0, len(block_list), 1000):
    res.append(block_list[i:i + 1000])
  return res


def create_value(block_list):
  res = []
  for domain in block_list:
    res.append({
      "value": domain,
      "created_at": datetime.datetime.utcnow().isoformat() + "Z"
    })
  return res


def create_lists(cf, block_list):
  split_block_list = blockListToMaxSize(block_list)
  i = 1
  for block_list_split in split_block_list:
    name = "automated_adblock_{}".format(i)
    while True:
      try:
        cf.accounts.gateway.lists.post(account_id,
                                       data={
                                         "name": name,
                                         "type": "DOMAIN",
                                         "description": "automated_adblock",
                                         "items":
                                         create_value(block_list_split)
                                       })
      except HTTPError as e:
        print(e)
        continue
      except CloudFlareAPIError as e:
        print(e)
        break
      break

    print("Progress: {}/{}".format(i, len(split_block_list)))
    i += 1


def get_block_list_ids(cf):
  gateway_lists = cf.accounts.gateway.lists.get(account_id,
                                                params={'per_page': 150})

  res = []
  for gateway_list in gateway_lists:
    if gateway_list["type"] == "DOMAIN" and gateway_list[
        "description"] == "automated_adblock":
      res.append(gateway_list["id"])

  return res


def create_gateway_policies(cf):
  i = 0
  block_list_ids = get_block_list_ids(cf)
  for block_id in block_list_ids:
    i += 1
    name = "automated_adblock_{}".format(i)
    block_str = "any(dns.domains[*] in {})".format("$" + block_id)
    while True:
      try:
        cf.accounts.gateway.rules.post(account_id,
                                       data={
                                         "name": name,
                                         "action": "block",
                                         "enabled": True,
                                         "precedence": 1000 + i,
                                         "filters": ["dns"],
                                         "description": "automated_adblock",
                                         "traffic": block_str
                                       })
      except HTTPError as e:
        print(e)
        continue
      except CloudFlareAPIError as e:
        print(e)
        break
      break

    print("Progress {}/{}".format(i, len(block_list_ids)))


def create_all(cf, block_list_url):
  block_list = get_block_list(block_list_url)
  print("Block list has {} domains".format(len(block_list)))

  print("Creating new lists")
  create_lists(cf, block_list)
  print("Created new lists")
  print("Creating new gateway policies")
  create_gateway_policies(cf)
  print("Created new gateway policies")


def get_gateway_policies_to_delete(cf):
  gateway_policies = cf.accounts.gateway.rules.get(account_id)

  to_delete = []
  for gateway_policy in gateway_policies:
    if gateway_policy["description"] == "automated_adblock":
      to_delete.append(gateway_policy["id"])

  return to_delete


def delete_old_gateway_policies(cf):
  for to_delete in get_gateway_policies_to_delete(cf):
    while True:
      try:
        cf.accounts.gateway.rules.delete(account_id, to_delete)
      except HTTPError as e:
        print(e)
        continue
      except CloudFlareAPIError as e:
        print(e)
        break
      break


def get_lists_to_delete(cf):
  gateway_lists = cf.accounts.gateway.lists.get(account_id)

  if gateway_lists is None:
    print("Error retrieving gateway lists.")
    return []

  to_delete = []
  for gateway_list in gateway_lists:
    if gateway_list["type"] == "DOMAIN" and gateway_list[
        "description"] == "automated_adblock":
      to_delete.append(gateway_list["id"])

  return to_delete


def delete_old_lists(cf):
  to_delete = get_lists_to_delete(cf)
  if not to_delete:
    print("No lists to delete.")
    return

  for list_id in to_delete:
    while True:
      try:
        cf.accounts.gateway.lists.delete(account_id, list_id)
      except HTTPError as e:
        print(e)
        continue
      except CloudFlareAPIError as e:
        print(e)
        break
      break


def delete_all(cf):
  print("Deleting old gateway policies")
  delete_old_gateway_policies(cf)
  print("Deleted old gateway policies")
  print("Deleting old lists")
  delete_old_lists(cf)
  print("Deleted old lists")


def main():
  CF = CloudFlare.CloudFlare(email=email, token=token)

  block_list_url = "https://raw.githubusercontent.com/MartinatorTime/Cloudflare-adblock-py/main/cloudflare/lists/blockdomains.txt"
  delete_all(CF)
  create_all(CF, block_list_url)


if __name__ == '__main__':
  main()
