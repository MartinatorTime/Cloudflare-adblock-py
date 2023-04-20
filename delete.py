from requests import HTTPError
from CloudFlare.exceptions import CloudFlareAPIError

from main import account_id


def GetGatewayPoliciesToDelete(cf):
    gateway_policies = cf.accounts.gateway.rules.get(account_id)

    to_delete = []
    for gateway_policy in gateway_policies:
        if gateway_policy["description"] == "automated_adblock":
            to_delete.append(gateway_policy["id"])

    return to_delete


def DeleteOldGatewayPolicies(cf):
    for to_delete in GetGatewayPoliciesToDelete(cf):
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


def GetListsToDelete(cf):
    gateway_lists = cf.accounts.gateway.lists.get(account_id)

    if gateway_lists is None:
        print("Error retrieving gateway lists.")
        return []

    to_delete = []
    for gateway_list in gateway_lists:
        if gateway_list["type"] == "DOMAIN" and gateway_list["description"] == "automated_adblock":
            to_delete.append(gateway_list["id"])

    return to_delete


def DeleteOldLists(cf):
    to_delete = GetListsToDelete(cf)
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


def DeleteAll(cf):
    print("Deleting old gateway policies")
    DeleteOldGatewayPolicies(cf)
    print("Deleted old gateway policies")
    print("Deleting old lists")
    DeleteOldLists(cf)
    print("Deleted old lists")


if __name__ == '__main__':
    # Initialize Cloudflare API client
    CF = CloudFlare.CloudFlare()

    DeleteAll(CF)