import os
import CloudFlare
import requests
from delete import DeleteAll
from create import CreateAll

def GetBlockList(block_list_url):
    block_list = requests.get(block_list_url).text.splitlines()
    return block_list

def main():
    try:
        token = os.environ['CF_API_TOKEN']
        email = os.environ['CF_API_EMAIL']
        account_id = os.environ['CF_API_ACCOUNT_ID']
    except KeyError:
        print('CF_API_TOKEN, CF_API_EMAIL or CF_API_ACCOUNT_ID environment variable not set')
        return

    block_list_url = "https://raw.githubusercontent.com/MartinatorTime/cloudflare-adblock/master/cloudflare/lists/pihole_domain_list.txt"
    block_list = GetBlockList(block_list_url)
    print("Block list has {} domains".format(len(block_list)))

    CF = CloudFlare.CloudFlare(email=email, token=token)
    DeleteAll(CF)
    CreateAll(CF, block_list)

if __name__ == '__main__':
    main()
