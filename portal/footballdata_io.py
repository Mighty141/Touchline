"""Footballdata.io fallback provider adapter. API keys are read only from environment."""
import os
import requests
from datetime import datetime, timezone

BASE = "https://footballdata.io/api/v1"

class FootballdataIOError(Exception):
    pass

def get(path, params=None):
    key = (os.environ.get('FOOTBALLDATA_IO_API_KEY') or os.environ.get('FOOTBALL_DATA_IO_API_KEY') or '').strip()
    if not key or key.lower().startswith(('your_', 'put_your_', 'replace_')):
        raise FootballdataIOError('Missing FOOTBALLDATA_IO_API_KEY. Add your existing Footballdata.io key to .env.')
    try:
        r = requests.get(f"{BASE}/{path.lstrip('/')}", params=params or {}, headers={'Authorization': f'Bearer {key}', 'Accept':'application/json'}, timeout=25)
        data = r.json()
    except requests.RequestException as e:
        raise FootballdataIOError(f'Footballdata.io connection failed: {e}') from e
    except ValueError as e:
        raise FootballdataIOError('Footballdata.io returned invalid JSON.') from e
    if not r.ok or (isinstance(data, dict) and data.get('success') is False):
        err = data.get('error', {}) if isinstance(data, dict) else {}
        msg = err.get('message') if isinstance(err, dict) else str(err)
        raise FootballdataIOError(f'Footballdata.io HTTP {r.status_code}: {msg or r.text[:200]}')
    return data

def rows(payload):
    data = payload.get('data', []) if isinstance(payload, dict) else []
    if isinstance(data, dict):
        for key in ('matches','teams','standings','seasons','leagues','results','events'):
            if isinstance(data.get(key), list): return data[key]
        return [data]
    return data if isinstance(data, list) else []

def get_premier_league(season_start):
    leagues = rows(get('/leagues', {'search':'Premier League', 'country':'England'}))
    league = next((x for x in leagues if 'premier league' in str(x.get('league_name') or x.get('name') or '').lower()), None)
    if not league:
        raise FootballdataIOError('Your Footballdata.io plan returned no English Premier League. Check league coverage.')
    league_id = league.get('league_id') or league.get('id')
    seasons = rows(get(f'/leagues/{league_id}/seasons'))
    season = next((s for s in seasons if str(s.get('year','')).startswith(str(season_start)) or str(s.get('season_year','')).startswith(str(season_start))), None)
    season_id = (season or {}).get('season_id') or (season or {}).get('id')
    # Some endpoints accept season year directly; prefer the public season ID if present.
    return str(league_id), season_id

def to_datetime(match):
    ts = match.get('date_unix') or match.get('timestamp')
    if ts:
        try: return datetime.fromtimestamp(int(ts), tz=timezone.utc)
        except (ValueError, TypeError, OSError): pass
    value = match.get('match_date') or match.get('date') or match.get('datetime') or match.get('kickoff')
    if not value: return None
    try: return datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    except (ValueError, TypeError): return None

def status_to_local(status):
    s = str(status or '').lower()
    if s in {'complete','completed','finished','ft','full_time','full time'}: return 'FT'
    if s in {'live','in_play','in-play','1h','2h','ht','half_time','halftime'}: return 'LIVE'
    if s in {'postponed','cancelled','canceled','abandoned','suspended'}: return 'POSTPONED'
    return 'UPCOMING'
