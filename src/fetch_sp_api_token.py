"""Fetch an Amazon SP-API access token using credentials stored in a .env file.

This script mirrors the documented cURL request by issuing a POST request to the
Amazon login endpoint with the client credentials and refresh token retrieved
from a local ``.env`` file. The file must define the following variables::

    SP_API_CLIENT_ID
    SP_API_SECRET
    SP_API_TOKEN

The resulting access token is printed to stdout. The entire JSON response is
also emitted to stderr for debugging purposes.
"""
from __future__ import annotations

import json
import os
import sys
from typing import Dict

import requests
from dotenv import load_dotenv

TOKEN_ENDPOINT = "https://api.amazon.com/auth/o2/token"
FORM_CONTENT_TYPE = "application/x-www-form-urlencoded;charset=UTF-8"


class MissingEnvironmentVariableError(RuntimeError):
    """Raised when a required environment variable cannot be located."""


def get_env_value(name: str) -> str:
    """Retrieve a configuration value from the environment."""

    try:
        return os.environ[name]
    except KeyError as exc:  # pragma: no cover - defensive branch
        raise MissingEnvironmentVariableError(
            f"Required variable '{name}' is not defined in .env or the environment."
        ) from exc


def build_request_payload(client_id: str, client_secret: str, refresh_token: str) -> Dict[str, str]:
    """Build the form payload for the token request."""

    return {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }


def fetch_access_token() -> str:
    """Execute the token request and return the access token string."""

    # Load environment variables from .env file
    load_dotenv()

    client_id = get_env_value("SP_API_CLIENT_ID")
    client_secret = get_env_value("SP_API_SECRET")
    refresh_token = get_env_value("SP_API_TOKEN")

    payload = build_request_payload(client_id, client_secret, refresh_token)

    headers = {"Content-Type": FORM_CONTENT_TYPE}

    try:
        response = requests.post(TOKEN_ENDPOINT, data=payload, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:  # pragma: no cover - network failures
        raise RuntimeError(f"Failed to fetch access token: {exc}") from exc

    response_text = response.text

    try:
        response_json = response.json()
    except (json.JSONDecodeError, ValueError) as exc:  # pragma: no cover - defensive branch
        raise RuntimeError(
            f"Amazon SP-API token endpoint returned non-JSON response: {response_text}"
        ) from exc

    try:
        access_token = response_json["access_token"]
    except KeyError as exc:  # pragma: no cover - defensive branch
        raise RuntimeError(
            "Response JSON is missing the 'access_token' field."
        ) from exc

    print(json.dumps(response_json, indent=2), file=sys.stderr)
    return access_token


if __name__ == "__main__":
    try:
        token = fetch_access_token()
    except MissingEnvironmentVariableError as error:
        print(error, file=sys.stderr)
        sys.exit(1)
    except Exception as error:  # pragma: no cover - unexpected failures
        print(f"Failed to retrieve access token: {error}", file=sys.stderr)
        sys.exit(1)

    print(token)
