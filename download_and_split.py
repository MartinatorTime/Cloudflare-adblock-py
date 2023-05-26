import requests
import sys

url = "https://raw.githubusercontent.com/MartinatorTime/Cloudflare-adblock-py/main/cloudflare/lists/hosts.txt"
response = requests.get(url)
domains = response.text.split('\n')

for i in range(0, len(domains), 1000):
    with open(f"list_{i//1000 + 1}.txt", "w") as f:
        f.write("\n".join(domains[i:i+1000]))
