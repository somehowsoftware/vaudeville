"""Minimal YouTrack client: credential loading + a paginated search call,
a generic request helper for single admin/issue calls, and a paginated list
helper for admin collections that outgrow one page.

Credentials come from env (YOUTRACK_API_BASE, YOUTRACK_API_KEY) or, as a
fallback, `~/.vaudeville/credentials.toml` under a `[youtrack]` table with
`api_base` and `api_key` keys. Future tools add their own top-level tables.
`search` returns raw issue dicts; `request` returns parsed JSON for any
single call (or None on a 204); `request_all` pages a collection endpoint
in full.
"""

from __future__ import annotations

import json
import os
import sys
import tomllib
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from vaudeville_core.backend import Request


def _read_credentials_file() -> tuple[str, str]:
    path = Path.home() / ".vaudeville" / "credentials.toml"
    if not path.exists():
        return "", ""
    with path.open("rb") as handle:
        config = tomllib.load(handle)
    youtrack = config.get("youtrack", {})
    if not isinstance(youtrack, dict):
        return "", ""
    api_base = youtrack.get("api_base", "")
    api_key = youtrack.get("api_key", "")
    return (api_base if isinstance(api_base, str) else ""), (
        api_key if isinstance(api_key, str) else ""
    )


def load_credentials() -> tuple[str, str]:
    url = os.environ.get("YOUTRACK_API_BASE", "")
    token = os.environ.get("YOUTRACK_API_KEY", "")
    if not url or not token:
        file_url, file_token = _read_credentials_file()
        url = url or file_url
        token = token or file_token
    if not url or not token:
        print(
            "Error: YouTrack credentials not found. Set YOUTRACK_API_BASE and "
            "YOUTRACK_API_KEY, or put them in ~/.vaudeville/credentials.toml.",
            file=sys.stderr,
        )
        sys.exit(1)
    return url.rstrip("/"), token


def search(
    query: str,
    fields: str,
    *,
    page_size: int = 200,
    timeout: int = 15,
) -> list[dict[str, Any]]:
    if page_size <= 0:
        raise ValueError(f"page_size must be positive, got {page_size}")
    url, token = load_credentials()
    results: list[dict[str, Any]] = []
    skip = 0
    while True:
        params = urllib.parse.urlencode(
            {"query": query, "fields": fields, "$top": page_size, "$skip": skip}
        )
        req = urllib.request.Request(
            f"{url}/issues?{params}",
            headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                page = json.loads(response.read().decode())
        except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError) as exc:
            print(f"Error: YouTrack request failed: {exc}", file=sys.stderr)
            sys.exit(1)
        if not isinstance(page, list):
            print("Error: unexpected response format from YouTrack.", file=sys.stderr)
            sys.exit(1)
        results.extend(page)
        if len(page) < page_size:
            return results
        skip += page_size


def request(
    method: str,
    path: str,
    *,
    json_body: Any = None,
    params: Mapping[str, str] | None = None,
    timeout: int = 15,
    allow_404: bool = False,
) -> Any:
    """Single-call API helper. `path` is appended to the API base verbatim.

    `allow_404=True` swaps the default exit-on-404 for a `None` return so
    callers can distinguish "this entity does not exist" from genuine
    transport errors. Useful for direct-lookup endpoints
    (`/admin/projects/{shortName}`, `/users/{login}`) where 404 carries
    information rather than indicating a bug.
    """
    url, token = load_credentials()
    full = f"{url}{path}"
    if params:
        full = f"{full}?{urllib.parse.urlencode(params)}"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    data: bytes | None = None
    if json_body is not None:
        data = json.dumps(json_body).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(full, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read().decode()
            return json.loads(body) if body else None
    except urllib.error.HTTPError as exc:
        if allow_404 and exc.code == 404:
            return None
        detail = exc.read().decode(errors="replace") if hasattr(exc, "read") else ""
        print(
            f"Error: YouTrack {method} {path} failed ({exc.code}): {detail}",
            file=sys.stderr,
        )
        sys.exit(1)
    except (urllib.error.URLError, json.JSONDecodeError) as exc:
        print(f"Error: YouTrack {method} {path} failed: {exc}", file=sys.stderr)
        sys.exit(1)


def request_all(
    path: str,
    *,
    fields: str,
    page_size: int = 200,
    timeout: int = 15,
) -> list[Any]:
    """A bare ``request`` returns only the server's default page, so a collection
    that outgrows one page silently truncates. Provisioning's idempotency turns on
    observing *every* existing bundle and field definition — a missed one re-plans
    a create that already exists — so its listing reads page in full through
    ``$top``/``$skip``.
    """
    if page_size <= 0:
        raise ValueError(f"page_size must be positive, got {page_size}")
    results: list[Any] = []
    skip = 0
    while True:
        page = request(
            "GET",
            path,
            params={"fields": fields, "$top": str(page_size), "$skip": str(skip)},
            timeout=timeout,
        )
        if not isinstance(page, list):
            print("Error: unexpected response format from YouTrack.", file=sys.stderr)
            sys.exit(1)
        results.extend(page)
        if len(page) < page_size:
            return results
        skip += page_size


def perform(req: Request) -> Any:
    return request(
        req.method,
        req.path,
        json_body=req.json_body,
        params=req.params,
        allow_404=req.allow_404,
    )
