"""API-Football v3 client. Official docs: https://www.api-football.com/documentation-v3"""
import os
import requests

BASE_URL = "https://v3.football.api-sports.io"


class FootballDataError(Exception):
    """A safe, user-readable API integration error."""


def api_get(path, params=None):
    token = (os.environ.get("API_FOOTBALL_KEY") or os.environ.get("FOOTBALL_API_KEY") or "").strip()
    if not token:
        raise FootballDataError("Missing API_FOOTBALL_KEY. Add your API-Football key to the project's .env file.")
    try:
        response = requests.get(
            f"{BASE_URL}/{path.lstrip('/')}",
            params=params or {},
            headers={"x-apisports-key": token, "Accept": "application/json"},
            timeout=20,
        )
    except requests.RequestException as exc:
        raise FootballDataError(f"Could not reach API-Football: {exc}") from exc
    try:
        payload = response.json()
    except ValueError:
        payload = None
    if response.status_code == 401:
        detail = _format_api_errors(payload) or "API returned HTTP 401."
        raise FootballDataError(
            f"API-Football authentication failed (401): {detail} "
            "Check that API_FOOTBALL_KEY is the active key from dashboard.api-football.com, "
            "with no quotes/spaces, and that you are not using a RapidAPI key with the direct API host."
        )
    if response.status_code == 403:
        detail = _format_api_errors(payload) or "API returned HTTP 403."
        raise FootballDataError(
            f"API-Football access forbidden (403): {detail} "
            "Check subscription status and endpoint/season coverage in the API-Football dashboard."
        )
    if response.status_code == 429:
        detail = _format_api_errors(payload) or "Rate limit exceeded."
        raise FootballDataError(f"API-Football rate limit reached: {detail} Check your daily/minute quota.")
    if not response.ok:
        detail = _format_api_errors(payload) or response.text[:250]
        raise FootballDataError(f"API-Football request failed ({response.status_code}): {detail}")
    if payload is None:
        raise FootballDataError("API-Football returned a response that was not valid JSON.")
    errors = payload.get("errors") if isinstance(payload, dict) else None
    if errors:
        if isinstance(errors, dict):
            message = "; ".join(f"{k}: {v}" for k, v in errors.items())
        elif isinstance(errors, list):
            message = "; ".join(str(x) for x in errors)
        else:
            message = str(errors)
        raise FootballDataError(f"API-Football: {message}")
    return payload


def _format_api_errors(payload):
    """Convert API-Football's error payload into a readable diagnostic."""
    if not isinstance(payload, dict):
        return ""
    errors = payload.get("errors")
    if isinstance(errors, dict):
        return "; ".join(f"{key}: {value}" for key, value in errors.items())
    if isinstance(errors, list):
        return "; ".join(str(value) for value in errors)
    if errors:
        return str(errors)
    return ""


def unwrap(payload):
    """Return the API-Football response array or unwrap compatible envelopes."""
    if isinstance(payload, dict):
        if isinstance(payload.get("response"), list):
            return payload["response"]
        if "data" in payload:
            return payload["data"]
    return payload


def find_list(payload, keys=()):
    obj = unwrap(payload)
    if isinstance(obj, list):
        return obj
    if isinstance(obj, dict):
        for key in keys:
            value = obj.get(key)
            if isinstance(value, list):
                return value
        for value in obj.values():
            if isinstance(value, list) and (not value or isinstance(value[0], dict)):
                return value
    return []


def first(item, *keys, default=None):
    if not isinstance(item, dict):
        return default
    for key in keys:
        value = item.get(key)
        if value is not None and value != "":
            return value
    return default


def object_id(item):
    value = first(item, "id", "team_id", "league_id", "match_id", "fixture_id", "season_id")
    return str(value) if value is not None else None


def team_name(item):
    return first(item, "name", "team_name", "display_name", "short_name", "shortName", default="")


def nested_team(item, side):
    if not isinstance(item, dict):
        return {}
    for key in (side, f"{side}_team", f"{side}Team"):
        value = item.get(key)
        if isinstance(value, dict):
            return value
    return {}
