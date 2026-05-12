#!/usr/bin/env python3
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent


def normalize_base_url(base_url: str) -> str:
    return base_url.rstrip("/")


def derive_domain(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Invalid URL: {url}")
    return parsed.hostname or parsed.netloc


def read_content(args: argparse.Namespace) -> str:
    if args.content_file:
        return Path(args.content_file).read_text(encoding="utf-8")
    if args.content is not None:
        return args.content
    if args.stdin_content:
        return sys.stdin.read()
    return ""


def request_json(method: str, url: str, headers: Dict[str, str], body: Optional[Dict[str, Any]] = None) -> Any:
    data = None
    request_headers = dict(headers)
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        request_headers["Content-Type"] = "application/json"

    request = Request(url, data=data, headers=request_headers, method=method)
    try:
        with urlopen(request) as response:
            raw = response.read().decode("utf-8")
    except HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} for {url}: {error_body}") from exc
    except URLError as exc:
        raise RuntimeError(f"Request failed for {url}: {exc}") from exc

    if not raw:
        return None

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def auth_headers(base_url: str, token: Optional[str], username: Optional[str], password: Optional[str]) -> Dict[str, str]:
    if token:
        return {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    if username and password:
        response = parse_api_result(
            request_json(
                "POST",
                f"{base_url}/api/auth/signin",
                {"Accept": "application/json"},
                {"username": username, "password": password},
            )
        )
        jwt = (response or {}).get("data")
        if not jwt:
            raise RuntimeError("Huntly signin succeeded but no JWT token was returned")
        return {"Authorization": f"Bearer {jwt}", "Accept": "application/json"}

    raise RuntimeError(
        "Missing Huntly auth. Provide HUNTLY_TOKEN or HUNTLY_USERNAME/HUNTLY_PASSWORD env vars"
    )


def parse_api_result(response: Any) -> Dict[str, Any]:
    if not isinstance(response, dict):
        raise RuntimeError(f"Unexpected API response: {response!r}")

    code = response.get("code")
    if code not in (None, 0):
        message = response.get("message") or response.get("msg") or "Unknown Huntly API error"
        raise RuntimeError(f"Huntly API returned code={code}: {message}")

    return response


def main() -> int:
    parser = argparse.ArgumentParser(description="Save content/page into Huntly via REST API")
    parser.add_argument("--url", required=True, help="Original content URL")
    parser.add_argument("--title", help="Content title")
    parser.add_argument("--description", help="Content description / summary")
    parser.add_argument("--author", help="Author name")
    parser.add_argument("--site-name", help="Site name")
    parser.add_argument("--favicon-url", help="Favicon URL")
    parser.add_argument("--domain", help="Source domain; derived from --url if omitted")
    parser.add_argument("--content", help="Inline HTML content")
    parser.add_argument("--content-file", help="Path to a file containing HTML content")
    parser.add_argument("--stdin-content", action="store_true", help="Read content from stdin")
    parser.add_argument("--save-mode", choices=["my-list", "read-later", "archive", "none"], default="my-list")
    parser.add_argument("--collection-id", type=int, help="Optional Huntly collection ID")
    parser.add_argument("--base-url", help="Huntly base URL, e.g. https://huntly.example.com")
    parser.add_argument("--token", help="JWT token for Huntly")
    parser.add_argument("--username", help="Huntly username")
    parser.add_argument("--password", help="Huntly password")
    args = parser.parse_args()

    config = {}  # no longer loading from JSON
    base_url = normalize_base_url(args.base_url or os.getenv("HUNTLY_BASE_URL", ""))
    if not base_url:
        raise RuntimeError("Missing Huntly base URL. Provide --base-url or HUNTLY_BASE_URL env var")

    token = args.token or os.getenv("HUNTLY_TOKEN", "")
    username = args.username or os.getenv("HUNTLY_USERNAME", "")
    password = args.password or os.getenv("HUNTLY_PASSWORD", "")
    headers = auth_headers(base_url, token, username, password)

    content = read_content(args)
    domain = args.domain or derive_domain(args.url)

    payload = {
        "title": args.title or "",
        "content": content,
        "url": args.url,
        "description": args.description or "",
        "author": args.author or "",
        "siteName": args.site_name or "",
        "domain": domain,
        "faviconUrl": args.favicon_url or "",
    }

    save_response = parse_api_result(request_json("POST", f"{base_url}/api/page/save", headers, payload))
    page_id = save_response.get("data")
    if not page_id:
        raise RuntimeError(f"Huntly did not return a page id: {save_response}")

    operations: Dict[str, Any] = {"page_save": save_response}

    if args.save_mode == "my-list":
        operations["library"] = parse_api_result(
            request_json("POST", f"{base_url}/api/page/saveToLibrary/{page_id}", headers)
        )
    elif args.save_mode == "read-later":
        operations["library"] = parse_api_result(
            request_json("POST", f"{base_url}/api/page/saveToLibrary/{page_id}", headers)
        )
        operations["read_later"] = parse_api_result(
            request_json("POST", f"{base_url}/api/page/readLater/{page_id}", headers)
        )
    elif args.save_mode == "archive":
        operations["library"] = parse_api_result(
            request_json("POST", f"{base_url}/api/page/archive/{page_id}", headers)
        )

    if args.collection_id is not None:
        operations["collection"] = parse_api_result(
            request_json(
                "PATCH",
                f"{base_url}/api/page/{page_id}/collection",
                headers,
                {"collectionId": args.collection_id},
            )
        )

    result = {
        "ok": True,
        "page_id": page_id,
        "url": args.url,
        "domain": domain,
        "save_mode": args.save_mode,
        "collection_id": args.collection_id,
        "operations": operations,
    }
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        json.dump({"ok": False, "error": str(exc)}, sys.stderr, ensure_ascii=False)
        sys.stderr.write("\n")
        raise SystemExit(1)
