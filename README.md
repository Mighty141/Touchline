# Touchline — Midnight Editorial Glass Edition (football-data.org only)

Touchline is a Django Premier League portal with a Midnight Editorial visual identity and translucent glass styling. **football-data.org is the sole football-data provider**; API-Football has been removed from the active configuration and runtime paths.

## Data source

The app reads the key from `FOOTBALL_DATA_ORG_API_KEY` in `.env` and requests data from football-data.org. League IDs, season IDs, event/statistics endpoints and data coverage are provider-dependent. The app does not invent results or statistics when the API does not return them.

## Quick start (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py sync_premier_league
python manage.py runserver
```

Open http://127.0.0.1:8000/.

The `.env` file is configured with the football-data.org key supplied earlier in this conversation. Keep it private and do not commit it. `.env.example` contains a placeholder only.

To choose the season, edit `FOOTBALL_DATA_ORG_SEASON` or run `python manage.py sync_premier_league --season 2026`.

## Match detail

Open a fixture to load match events and available team statistics. Player-level match data is shown only if football-data.org exposes it through the account's available endpoints. If the provider plan does not return a data category, Touchline displays an unavailable/empty state rather than mock statistics.

## Included Web Technology demos

The `demos/` folder contains standalone examples for AngularJS, Python CGI GET/POST, Node.js JSON API, MySQL CRUD, and Python MySQL Connector.

## Notes

- Default database: SQLite (`db.sqlite3`).
- `python manage.py migrate` creates the database schema.
- `python manage.py sync_premier_league` imports real provider data.
- API access and coverage depend on football-data.org, your subscription, and the selected season.
- Club crests use the logo URLs returned by football-data.org when provided.
