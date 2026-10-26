"""Client for the official football-data.org API v4."""
import os
from datetime import datetime
import requests

BASE = "https://api.football-data.org/v4"

class FootballDataOrgError(Exception):
    pass

def get(path, params=None):
    token = (os.environ.get("FOOTBALL_DATA_ORG_API_KEY") or os.environ.get("FOOTBALLDATA_ORG_API_KEY") or "").strip()
    if not token or token.lower().startswith(("your_", "put_your_", "replace_")):
        raise FootballDataOrgError("Missing FOOTBALL_DATA_ORG_API_KEY. Add your football-data.org token to .env.")
    try:
        response = requests.get(f"{BASE}/{path.lstrip('/')}", params=params or {}, headers={"X-Auth-Token": token, "Accept": "application/json", "X-Unfold-Goals": "true"}, timeout=25)
    except requests.RequestException as exc:
        raise FootballDataOrgError(f"football-data.org connection failed: {exc}") from exc
    try:
        payload = response.json()
    except ValueError:
        payload = {}
    if not response.ok:
        message = payload.get("message") if isinstance(payload, dict) else ""
        hints = {401: "Token rejected. Check your football-data.org API token.", 403: "This resource or season is not available on your football-data.org plan.", 429: "API request limit reached; wait for the quota reset."}
        raise FootballDataOrgError(f"football-data.org HTTP {response.status_code}: {message or hints.get(response.status_code, response.text[:200])}")
    return payload

def rows(payload, key):
    value = payload.get(key, []) if isinstance(payload, dict) else []
    return value if isinstance(value, list) else []

def parse_datetime(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None

def local_status(status):
    return {"FINISHED": "FT", "IN_PLAY": "LIVE", "PAUSED": "LIVE", "SCHEDULED": "UPCOMING", "TIMED": "UPCOMING", "POSTPONED": "POSTPONED", "CANCELLED": "POSTPONED", "SUSPENDED": "POSTPONED", "AWARDED": "FT"}.get(str(status or "").upper(), "UPCOMING")
