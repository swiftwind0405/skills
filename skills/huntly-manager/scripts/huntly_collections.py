#!/usr/bin/env python3
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent


def normalize_base_url(base_url: str) -> str:
    return base_url.rstrip("/")


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


def parse_api_result(response: Any) -> Any:
    if isinstance(response, dict) and "error" in response:
        error = response.get("error") or {}
        message = error.get("message") or response
        raise RuntimeError(str(message))

    if not isinstance(response, dict):
        return response

    code = response.get("code")
    if code not in (None, 0):
        message = response.get("message") or response.get("msg") or "Unknown Huntly API error"
        raise RuntimeError(f"Huntly API returned code={code}: {message}")

    return response.get("data", response)


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
        jwt = response if isinstance(response, str) else (response or {}).get("token")
        if not jwt:
            raise RuntimeError("Huntly signin succeeded but no JWT token was returned")
        return {"Authorization": f"Bearer {jwt}", "Accept": "application/json"}

    raise RuntimeError(
        "Missing Huntly auth. Provide HUNTLY_TOKEN or HUNTLY_USERNAME/HUNTLY_PASSWORD env vars"
    )


def build_client(args: argparse.Namespace) -> tuple[str, Dict[str, str]]:
    base_url = normalize_base_url(args.base_url or os.getenv("HUNTLY_BASE_URL", ""))
    if not base_url:
        raise RuntimeError("Missing Huntly base URL. Provide --base-url or HUNTLY_BASE_URL env var")

    token = args.token or os.getenv("HUNTLY_TOKEN", "")
    username = args.username or os.getenv("HUNTLY_USERNAME", "")
    password = args.password or os.getenv("HUNTLY_PASSWORD", "")
    headers = auth_headers(base_url, token, username, password)
    return base_url, headers


def api_get(base_url: str, headers: Dict[str, str], path: str) -> Any:
    return parse_api_result(request_json("GET", f"{base_url}/api/{path}", headers))


def api_post(base_url: str, headers: Dict[str, str], path: str, body: Dict[str, Any]) -> Any:
    return parse_api_result(request_json("POST", f"{base_url}/api/{path}", headers, body))


def api_put(base_url: str, headers: Dict[str, str], path: str, body: Dict[str, Any]) -> Any:
    return parse_api_result(request_json("PUT", f"{base_url}/api/{path}", headers, body))


def flatten_collections(collections: List[Dict[str, Any]], group_name: str, path_prefix: str = "") -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for collection in collections:
        path = f"{path_prefix}/{collection['name']}" if path_prefix else collection["name"]
        rows.append({
            "id": collection["id"],
            "groupId": collection.get("groupId"),
            "parentId": collection.get("parentId"),
            "name": collection["name"],
            "path": path,
            "groupName": group_name,
            "pageCount": collection.get("pageCount"),
            "displaySequence": collection.get("displaySequence"),
        })
        rows.extend(flatten_collections(collection.get("children", []), group_name, path))
    return rows


def get_tree(base_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
    tree = api_get(base_url, headers, "collections/tree")
    if not isinstance(tree, dict):
        raise RuntimeError(f"Unexpected collections/tree response: {tree!r}")
    return tree


def find_group(tree: Dict[str, Any], group_id: Optional[int], group_name: Optional[str]) -> Dict[str, Any]:
    groups = tree.get("groups") or []
    if group_id is not None:
        for group in groups:
            if group.get("id") == group_id:
                return group
        raise RuntimeError(f"Collection group id={group_id} not found")
    if group_name:
        matches = [g for g in groups if g.get("name") == group_name]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            raise RuntimeError(f"Multiple groups matched name '{group_name}'")
        raise RuntimeError(f"Collection group name '{group_name}' not found")
    raise RuntimeError("Need either group_id or group_name")


def find_collection_by_id(collections: List[Dict[str, Any]], target_id: int) -> Optional[Dict[str, Any]]:
    for collection in collections:
        if collection.get("id") == target_id:
            return collection
        found = find_collection_by_id(collection.get("children", []), target_id)
        if found:
            return found
    return None


def find_collection_by_path(collections: List[Dict[str, Any]], path: str) -> Optional[Dict[str, Any]]:
    normalized = [part for part in path.split("/") if part]
    current_list = collections
    current: Optional[Dict[str, Any]] = None
    for name in normalized:
        current = next((c for c in current_list if c.get("name") == name), None)
        if current is None:
            return None
        current_list = current.get("children", [])
    return current


def get_parent_and_siblings(group: Dict[str, Any], parent_id: Optional[int]) -> tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
    if parent_id is None:
        return None, group.get("collections", [])
    parent = find_collection_by_id(group.get("collections", []), parent_id)
    if parent is None:
        raise RuntimeError(f"Parent collection id={parent_id} not found in group {group.get('name')}")
    return parent, parent.get("children", [])


def resolve_group_and_parent(tree: Dict[str, Any], args: argparse.Namespace) -> tuple[Dict[str, Any], Optional[int]]:
    group = find_group(tree, getattr(args, "group_id", None), getattr(args, "group_name", None))
    parent_id = getattr(args, "parent_id", None)
    parent_path = getattr(args, "parent_path", None)
    if parent_path:
        parent = find_collection_by_path(group.get("collections", []), parent_path)
        if parent is None:
            raise RuntimeError(f"Parent path '{parent_path}' not found in group {group.get('name')}")
        parent_id = parent.get("id")
    return group, parent_id


def cmd_tree(base_url: str, headers: Dict[str, str], args: argparse.Namespace) -> Dict[str, Any]:
    tree = get_tree(base_url, headers)
    if args.flat:
        rows: List[Dict[str, Any]] = []
        for group in tree.get("groups", []):
            rows.extend(flatten_collections(group.get("collections", []), group.get("name", "")))
        return {
            "ok": True,
            "unsortedCount": tree.get("unsortedCount"),
            "groups": [{"id": g.get("id"), "name": g.get("name"), "collectionCount": len(flatten_collections(g.get("collections", []), g.get("name", "")))} for g in tree.get("groups", [])],
            "collections": rows,
        }
    return {"ok": True, "tree": tree}


def cmd_groups(base_url: str, headers: Dict[str, str], _args: argparse.Namespace) -> Dict[str, Any]:
    groups = api_get(base_url, headers, "collection-groups")
    return {"ok": True, "groups": groups}


def cmd_create_group(base_url: str, headers: Dict[str, str], args: argparse.Namespace) -> Dict[str, Any]:
    payload = {"name": args.name}
    if args.icon is not None:
        payload["icon"] = args.icon
    if args.color is not None:
        payload["color"] = args.color
    group = api_post(base_url, headers, "collection-groups", payload)
    return {"ok": True, "group": group}


def cmd_update_group(base_url: str, headers: Dict[str, str], args: argparse.Namespace) -> Dict[str, Any]:
    payload: Dict[str, Any] = {}
    if args.name is not None:
        payload["name"] = args.name
    if args.icon is not None:
        payload["icon"] = args.icon
    if args.color is not None:
        payload["color"] = args.color
    if not payload:
        raise RuntimeError("No updates provided for group")
    group = api_put(base_url, headers, f"collection-groups/{args.group_id}", payload)
    return {"ok": True, "group": group}


def cmd_get_collection(base_url: str, headers: Dict[str, str], args: argparse.Namespace) -> Dict[str, Any]:
    tree = get_tree(base_url, headers)
    if args.collection_id is not None:
        for group in tree.get("groups", []):
            collection = find_collection_by_id(group.get("collections", []), args.collection_id)
            if collection:
                return {"ok": True, "group": {"id": group.get("id"), "name": group.get("name")}, "collection": collection}
        raise RuntimeError(f"Collection id={args.collection_id} not found")

    group = find_group(tree, args.group_id, args.group_name)
    collection = find_collection_by_path(group.get("collections", []), args.path)
    if not collection:
        raise RuntimeError(f"Collection path '{args.path}' not found in group {group.get('name')}")
    return {"ok": True, "group": {"id": group.get("id"), "name": group.get("name")}, "collection": collection}


def cmd_create_collection(base_url: str, headers: Dict[str, str], args: argparse.Namespace) -> Dict[str, Any]:
    tree = get_tree(base_url, headers)
    group, parent_id = resolve_group_and_parent(tree, args)
    _parent, siblings = get_parent_and_siblings(group, parent_id)

    if args.ensure_unique:
        existing = next((c for c in siblings if c.get("name") == args.name), None)
        if existing:
            return {
                "ok": True,
                "created": False,
                "reason": "already_exists",
                "group": {"id": group.get("id"), "name": group.get("name")},
                "collection": existing,
            }

    payload = {
        "groupId": group.get("id"),
        "parentId": parent_id,
        "name": args.name,
    }
    if args.icon is not None:
        payload["icon"] = args.icon
    if args.color is not None:
        payload["color"] = args.color
    collection = api_post(base_url, headers, "collections", payload)
    return {
        "ok": True,
        "created": True,
        "group": {"id": group.get("id"), "name": group.get("name")},
        "collection": collection,
    }


def cmd_update_collection(base_url: str, headers: Dict[str, str], args: argparse.Namespace) -> Dict[str, Any]:
    payload: Dict[str, Any] = {}
    if args.name is not None:
        payload["name"] = args.name
    if args.icon is not None:
        payload["icon"] = args.icon
    if args.color is not None:
        payload["color"] = args.color
    if args.new_group_id is not None:
        payload["groupId"] = args.new_group_id
    if args.new_parent_id is not None:
        payload["parentId"] = args.new_parent_id
    if not payload:
        raise RuntimeError("No updates provided for collection")
    collection = api_put(base_url, headers, f"collections/{args.collection_id}", payload)
    return {"ok": True, "collection": collection}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage Huntly collection groups and collections via REST API")
    parser.add_argument("--base-url", help="Huntly base URL, e.g. https://huntly.example.com")
    parser.add_argument("--token", help="JWT token for Huntly")
    parser.add_argument("--username", help="Huntly username")
    parser.add_argument("--password", help="Huntly password")

    subparsers = parser.add_subparsers(dest="command", required=True)

    tree = subparsers.add_parser("tree", help="Fetch collection tree")
    tree.add_argument("--flat", action="store_true", help="Flatten collections into rows with paths")
    tree.set_defaults(handler=cmd_tree)

    groups = subparsers.add_parser("groups", help="List collection groups")
    groups.set_defaults(handler=cmd_groups)

    create_group = subparsers.add_parser("create-group", help="Create a collection group")
    create_group.add_argument("--name", required=True)
    create_group.add_argument("--icon")
    create_group.add_argument("--color")
    create_group.set_defaults(handler=cmd_create_group)

    update_group = subparsers.add_parser("update-group", help="Update a collection group")
    update_group.add_argument("--group-id", type=int, required=True)
    update_group.add_argument("--name")
    update_group.add_argument("--icon")
    update_group.add_argument("--color")
    update_group.set_defaults(handler=cmd_update_group)

    get_collection = subparsers.add_parser("get-collection", help="Query a collection by id or path")
    get_collection.add_argument("--collection-id", type=int)
    get_collection.add_argument("--group-id", type=int)
    get_collection.add_argument("--group-name")
    get_collection.add_argument("--path", help="Slash-separated collection path inside a group, e.g. items/ai")
    get_collection.set_defaults(handler=cmd_get_collection)

    create_collection = subparsers.add_parser("create-collection", help="Create a collection under a group or parent collection")
    create_collection.add_argument("--group-id", type=int)
    create_collection.add_argument("--group-name")
    create_collection.add_argument("--parent-id", type=int)
    create_collection.add_argument("--parent-path", help="Slash-separated parent path inside the chosen group")
    create_collection.add_argument("--name", required=True)
    create_collection.add_argument("--icon")
    create_collection.add_argument("--color")
    create_collection.add_argument("--ensure-unique", action="store_true", help="Return the existing sibling collection instead of creating a duplicate")
    create_collection.set_defaults(handler=cmd_create_collection)

    update_collection = subparsers.add_parser("update-collection", help="Update a collection")
    update_collection.add_argument("--collection-id", type=int, required=True)
    update_collection.add_argument("--name")
    update_collection.add_argument("--icon")
    update_collection.add_argument("--color")
    update_collection.add_argument("--new-group-id", type=int)
    update_collection.add_argument("--new-parent-id", type=int)
    update_collection.set_defaults(handler=cmd_update_collection)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    base_url, headers = build_client(args)
    result = args.handler(base_url, headers, args)
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
