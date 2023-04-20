import requests
import json

# Set your email and API key
email = "your-email"
api_key = "your-api"

# Set the endpoint for the API
endpoint = "https://api.cloudflare.com/client/v4/accounts"

# Set the headers for the API request
headers = {
    "X-Auth-Email": email,
    "X-Auth-Key": api_key,
    "Content-Type": "application/json"
}

# Make a request to get a list of all accounts
response = requests.get(endpoint, headers=headers)

# Check if the API call was successful
if response.status_code != 200:
    print(f"Error: {response.status_code} - {response.text}")
else:
    # Parse the response JSON and get the account ID of the first account
    data = json.loads(response.text)
    if data is None or "result" not in data or len(data["result"]) == 0:
        print("Error: API response did not contain any accounts.")
    else:
        account_id = data["result"][0]["id"]
        print(f"Your account ID is {account_id}.")
