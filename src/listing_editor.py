from pathlib import Path
import json
import sys
import requests

from fetch_sp_api_token import MissingEnvironmentVariableError, fetch_access_token

sandbox_endpoints = {
    "NA": "sandbox.sellingpartnerapi-na.amazon.com",
    "EU": "sandbox.sellingpartnerapi-eu.amazon.com",
    "FE": "sandbox.sellingpartnerapi-fe.amazon.com",
}

def fetch_example(sandbox_endpoints, token):
    endpoint = sandbox_endpoints["NA"]
    url = f"https://{endpoint}/orders/v0/orders"
    params = {
        "MarketplaceIds": "ATVPDKIKX0DER",
        "CreatedAfter": "TEST_CASE_200"
    }

    headers = {
        "x-amz-access-token": token,
        "Content-Type": "application/json",
        "User-Agent": "My-Testing-App/1.0"
    }

    response = requests.get(url, headers=headers, params=params)

    print(response.status_code)
    return response.json()  # or response.text if not JSON

if __name__ == "__main__":
    try:
        token = fetch_access_token()
    except MissingEnvironmentVariableError as error:
        print(error, file=sys.stderr)
        sys.exit(1)
    except Exception as error:  # pragma: no cover - unexpected failures
        print(f"Failed to retrieve access token: {error}", file=sys.stderr)
        sys.exit(1)

    response = fetch_example(sandbox_endpoints, token)
    print(json.dumps(response, indent=2))

