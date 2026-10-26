from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from portal.models import Team, Player, Match
from portal.football_data_org import get, rows, parse_datetime, local_status, FootballDataOrgError

PALETTE = ["#e84393", "#0984e3", "#00b894", "#ff6b6b", "#6c5ce7", "#fdcb6e", "#00cec9"]

def number(value, fallback=0):
    try:
        return int(value) if value is not None else fallback
    except (TypeError, ValueError):
        return fallback

class Command(BaseCommand):
    help = "Sync real Premier League data from football-data.org API v4 only."

    def add_arguments(self, parser):
        parser.add_argument("--season", type=int, default=None, help="Season start year, e.g. 2026 for 2026/27.")

    def handle(self, *args, **options):
        import os
        season = options["season"] or int(os.environ.get("FOOTBALL_DATA_ORG_SEASON", "2026"))
        try:
            self._sync(season)
        except FootballDataOrgError as exc:
            raise CommandError(str(exc)) from exc
        except Exception as exc:
            raise CommandError(f"football-data.org sync failed: {exc}") from exc

    @transaction.atomic
    def _sync(self, season_year):
        self.stdout.write(f"Fetching Premier League {season_year}/{season_year + 1} from football-data.org API v4...")
        teams_raw = rows(get("/competitions/PL/teams", {"season": season_year}), "teams")
        matches_raw = rows(get("/competitions/PL/matches", {"season": season_year}), "matches")
        standings_raw = []
        try:
            standings_payload = get("/competitions/PL/standings", {"season": season_year})
            for table in rows(standings_payload, "standings"):
                if table.get("type") == "TOTAL":
                    standings_raw = table.get("table", [])
                    break
        except FootballDataOrgError as exc:
            self.stdout.write(self.style.WARNING(f"Standings unavailable; calculating from synced results where possible: {exc}"))
        if not teams_raw:
            # Some plans expose clubs via the competition match payload even when the team endpoint is restricted.
            seen = {}
            for match in matches_raw:
                for side in (match.get("homeTeam") or {}, match.get("awayTeam") or {}):
                    if side.get("id") is not None:
                        seen[str(side["id"])] = side
            teams_raw = list(seen.values())
        if not teams_raw or not matches_raw:
            raise FootballDataOrgError("No Premier League clubs or matches were returned. Check your plan's PL/current-season coverage.")

        local_by_api_id = {}
        for index, raw in enumerate(teams_raw):
            tid, name = raw.get("id"), raw.get("name")
            if tid is None or not name:
                continue
            crest = raw.get("crest") or f"https://crests.football-data.org/{tid}.png"
            short = raw.get("tla") or raw.get("shortName") or name[:3]
            defaults = {
                "name": name, "short_name": str(short).upper()[:12], "color": PALETTE[index % len(PALETTE)],
                "crest_url": crest, "city": (raw.get("area") or {}).get("name", "")
            }
            # Older/demo databases may already contain this club by name but have no
            # football-data.org api_id. Reuse that row instead of inserting a duplicate
            # name (Team.name is unique), then attach the provider ID.
            team = Team.objects.filter(api_id=str(tid)).first()
            if team is None:
                team = Team.objects.filter(name__iexact=name).first()
            if team is None:
                team = Team(**defaults, api_id=str(tid))
            else:
                for field, value in defaults.items():
                    setattr(team, field, value)
                team.api_id = str(tid)
            team.save()
            local_by_api_id[str(tid)] = team

        for index, row in enumerate(standings_raw, start=1):
            team_data = row.get("team") or {}
            team = local_by_api_id.get(str(team_data.get("id", "")))
            if not team:
                continue
            team.table_position = number(row.get("position"), index)
            team.played = number(row.get("playedGames"))
            team.wins = number(row.get("won"))
            team.draws = number(row.get("draw"))
            team.losses = number(row.get("lost"))
            team.goals_for = number(row.get("goalsFor"))
            team.goals_against = number(row.get("goalsAgainst"))
            team.points = number(row.get("points"))
            team.save()

        imported_ids, imported = set(), 0
        for item in matches_raw:
            home_data, away_data = item.get("homeTeam") or {}, item.get("awayTeam") or {}
            home = local_by_api_id.get(str(home_data.get("id", "")))
            away = local_by_api_id.get(str(away_data.get("id", "")))
            dt = parse_datetime(item.get("utcDate"))
            mid = item.get("id")
            if not home or not away or not dt or mid is None:
                continue
            score = item.get("score") or {}
            full = score.get("fullTime") or {}
            half = score.get("halfTime") or {}
            goals = item.get("goals") or []
            bookings = item.get("bookings") or []
            substitutions = item.get("substitutions") or []
            detail = {**item, "_touchline_provider": "football_data_org", "touchline_goals": goals,
                      "touchline_bookings": bookings, "touchline_substitutions": substitutions}
            defaults = {
                "home_team": home, "away_team": away, "match_date": dt,
                "home_score": number(full.get("home")), "away_score": number(full.get("away")),
                "competition": "Premier League", "status": local_status(item.get("status")),
                "venue": str(item.get("venue") or ""), "matchweek": str(item.get("matchday") or ""),
                "round_name": str(item.get("stage") or item.get("group") or ""),
                "halftime_home_score": half.get("home"), "halftime_away_score": half.get("away"),
                "detail_snapshot": detail,
            }
            Match.objects.update_or_create(api_match_id=str(mid), defaults=defaults)
            imported_ids.add(str(mid)); imported += 1
        if not imported:
            raise FootballDataOrgError("Fixtures were returned but none could be mapped to local clubs. Existing records were preserved.")
        Match.objects.filter(competition="Premier League").exclude(api_match_id__in=imported_ids).delete()
        Team.objects.exclude(id__in=[team.id for team in local_by_api_id.values()]).delete()
        Player.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f"Synced football-data.org Premier League {season_year}/{season_year + 1}: {len(local_by_api_id)} clubs and {imported} fixtures/results."))
        self.stdout.write("Club crests, standings, scores and goal/card/substitution events are sourced from football-data.org where available.")
