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
from pathlib import Path
from typing import Dict
from urllib import parse, request

TOKEN_ENDPOINT = "https://api.amazon.com/auth/o2/token"
FORM_CONTENT_TYPE = "application/x-www-form-urlencoded;charset=UTF-8"
ENV_FILENAME = ".env"


class MissingEnvironmentVariableError(RuntimeError):
    """Raised when a required environment variable cannot be located."""


def load_env_file(path: Path) -> Dict[str, str]:
    """Parse a ``.env`` file into a dictionary.

    The parser intentionally keeps the implementation light-weight so that the
    script has no third-party dependencies. Blank lines and comments beginning
    with ``#`` are ignored, and values may contain ``=`` characters.
    """

    values: Dict[str, str] = {}
    if not path.exists():
        return values

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if "=" not in stripped:
            continue

        name, value = stripped.split("=", 1)
        values[name.strip()] = value.strip()

    return values


def get_env_value(name: str, env_file_values: Dict[str, str]) -> str:
    """Retrieve a configuration value from ``.env`` or the process env."""

    if name in env_file_values and env_file_values[name]:
        return env_file_values[name]

    try:
        return os.environ[name]
    except KeyError as exc:  # pragma: no cover - defensive branch
        raise MissingEnvironmentVariableError(
            f"Required variable '{name}' is not defined in {ENV_FILENAME} or the environment."
        ) from exc


def build_request_payload(client_id: str, client_secret: str, refresh_token: str) -> bytes:
    """Build the form-encoded payload for the token request."""

    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    return parse.urlencode(payload).encode("utf-8")


def fetch_access_token() -> str:
    """Execute the token request and return the access token string."""

    env_values = load_env_file(Path.cwd() / ENV_FILENAME)

    client_id = get_env_value("SP_API_CLIENT_ID", env_values)
    client_secret = get_env_value("SP_API_SECRET", env_values)
    refresh_token = get_env_value("SP_API_TOKEN", env_values)

    payload = build_request_payload(client_id, client_secret, refresh_token)

    req = request.Request(TOKEN_ENDPOINT, data=payload, method="POST")
    req.add_header("Content-Type", FORM_CONTENT_TYPE)

    with request.urlopen(req) as response:
        response_text = response.read().decode("utf-8")

    try:
        response_json = json.loads(response_text)
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive branch
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
