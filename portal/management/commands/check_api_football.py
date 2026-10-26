from django.core.management.base import BaseCommand, CommandError
from portal.api_client import api_get, find_list, FootballDataError

class Command(BaseCommand):
    help = "Check API-Football key/subscription and Premier League season coverage."

    def add_arguments(self, parser):
        parser.add_argument("--season", type=int, default=None, help="Season start year; defaults to API_FOOTBALL_SEASON or 2026.")

    def handle(self, *args, **options):
        import os
        season = options["season"] or int(os.environ.get("API_FOOTBALL_SEASON", "2026"))
        self.stdout.write("Checking API-Football account status (this endpoint does not count against daily quota)...")
        try:
            status = api_get("/status")
            response = status.get("response", {}) if isinstance(status, dict) else {}
            account = response.get("account", {}) if isinstance(response, dict) else {}
            subscription = response.get("subscription", {}) if isinstance(response, dict) else {}
            requests_info = response.get("requests", {}) if isinstance(response, dict) else {}
            self.stdout.write(self.style.SUCCESS("API key accepted."))
            self.stdout.write(f"Account: {account.get('email') or account.get('firstname') or 'available'}")
            self.stdout.write(f"Plan: {subscription.get('plan', 'unknown')} | active: {subscription.get('active', 'unknown')} | expires: {subscription.get('end', 'unknown')}")
            self.stdout.write(f"Daily requests: {requests_info.get('current', '?')} / {requests_info.get('limit_day', '?')}")
            self.stdout.write(f"Checking Premier League (league 39), season {season}/{str(season + 1)[-2:]} coverage...")
            leagues = find_list(api_get("/leagues", {"id": 39, "season": season}))
            if not leagues:
                self.stdout.write(self.style.WARNING("Key works, but the API returned no Premier League record for this season."))
                return
            item = leagues[0]
            league = item.get("league", {})
            season_rows = item.get("seasons", []) or []
            chosen = next((x for x in season_rows if int(x.get("year", -1)) == season), {})
            coverage = chosen.get("coverage", {})
            fixtures = coverage.get("fixtures", {})
            self.stdout.write(f"Competition: {league.get('name', 'Premier League')} (ID {league.get('id', 39)})")
            self.stdout.write(f"Coverage: events={fixtures.get('events', 'unknown')}, lineups={fixtures.get('lineups', 'unknown')}, match statistics={fixtures.get('statistics_fixtures', 'unknown')}, player statistics={fixtures.get('statistics_players', 'unknown')}")
            if fixtures.get("statistics_fixtures") is False or fixtures.get("statistics_players") is False:
                self.stdout.write(self.style.WARNING("Your selected season's coverage flags indicate some deep stats are unavailable. Event/statistics coverage can vary by match."))
        except FootballDataError as exc:
            raise CommandError(str(exc)) from exc
