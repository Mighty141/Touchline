from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Team, Player, Match

REAL_COMPETITION = "Premier League"


def premier_league_teams():
    return Team.objects.filter(
        Q(home_matches__competition=REAL_COMPETITION) | Q(away_matches__competition=REAL_COMPETITION)
    ).distinct()


def home(request):
    query = request.GET.get("q", "").strip()
    real_matches = Match.objects.filter(competition=REAL_COMPETITION)
    is_real_data = real_matches.exists()
    teams = premier_league_teams() if is_real_data else Team.objects.none()
    players = Player.objects.filter(team__in=teams).select_related("team") if is_real_data else Player.objects.none()
    if query:
        teams = teams.filter(name__icontains=query)
        players = players.filter(name__icontains=query)

    upcoming = real_matches.filter(status__in=["UPCOMING", "LIVE", "POSTPONED"]).select_related("home_team", "away_team").order_by("match_date")
    recent = real_matches.filter(status="FT").select_related("home_team", "away_team").order_by("-match_date")
    matches = list(upcoming[:3]) + list(recent[:3])

    # Prefer the provider's official table. Fall back to calculating from imported results only
    # if the API did not supply any usable standings rows.
    table = []
    ordered_teams = list(teams.order_by("table_position", "-points", "-goals_for", "name"))
    if ordered_teams and any(t.table_position or t.played or t.points for t in ordered_teams):
        for team in ordered_teams:
            table.append({"team": team, "played": team.played, "wins": team.wins, "draws": team.draws,
                          "losses": team.losses, "gf": team.goals_for, "ga": team.goals_against,
                          "gd": team.goal_difference, "points": team.points,
                          "position": team.table_position})
        table.sort(key=lambda row: (row["position"] or 999, -row["points"], -row["gd"], -row["gf"]))
    else:
        for team in ordered_teams:
            played = list(real_matches.filter(status="FT", home_team=team)) + list(real_matches.filter(status="FT", away_team=team))
            wins = draws = losses = gf = ga = points = 0
            for match in played:
                own, opp = (match.home_score, match.away_score) if match.home_team_id == team.id else (match.away_score, match.home_score)
                gf += own; ga += opp
                if own > opp: wins += 1; points += 3
                elif own == opp: draws += 1; points += 1
                else: losses += 1
            table.append({"team": team, "played": len(played), "wins": wins, "draws": draws,
                          "losses": losses, "gf": gf, "ga": ga, "gd": gf-ga, "points": points, "position": 0})
        table.sort(key=lambda row: (row["points"], row["gd"], row["gf"]), reverse=True)

    return render(request, "portal/home.html", {
        "teams": teams, "players": players.order_by("-goals", "name")[:8], "matches": matches,
        "table": table, "query": query, "team_count": teams.count(), "player_count": players.count(),
        "match_count": real_matches.count(), "completed_count": real_matches.filter(status="FT").count(), "is_real_data": is_real_data,
        "season_label": "Current Premier League season" if is_real_data else "Awaiting API sync",
    })


def matches(request):
    qs = Match.objects.filter(competition=REAL_COMPETITION).select_related("home_team", "away_team")
    items = list(qs.filter(status__in=["LIVE", "UPCOMING", "POSTPONED"]).order_by("match_date")) + list(qs.filter(status="FT").order_by("-match_date"))
    return render(request, "portal/matches.html", {"matches": items})


def match_detail(request, match_id):
    match = get_object_or_404(Match.objects.select_related("home_team", "away_team"), pk=match_id, competition=REAL_COMPETITION)
    snapshot = match.detail_snapshot if isinstance(match.detail_snapshot, dict) else {}
    events, stats, players, api_error = [], [], [], ""

    # football-data.org v4 provides goals, bookings and substitutions in the match resource.
    # It does not provide possession/shots/player match-stat tables on the standard match endpoint.
    goals = snapshot.get("touchline_goals", snapshot.get("goals", [])) or []
    bookings = snapshot.get("touchline_bookings", snapshot.get("bookings", [])) or []
    substitutions = snapshot.get("touchline_substitutions", snapshot.get("substitutions", [])) or []
    for goal in goals:
        scorer = goal.get("scorer") or {}
        assist = goal.get("assist") or {}
        team = goal.get("team") or {}
        minute = goal.get("minute")
        if goal.get("injuryTime"):
            minute = f"{minute}+{goal.get('injuryTime')}"
        events.append({"minute": str(minute or "—"), "player": scorer.get("name", ""),
                       "assist": assist.get("name", ""), "team": team.get("name", ""),
                       "type": goal.get("type", "Goal"), "detail": "", "is_goal": True})
    for booking in bookings:
        player = booking.get("player") or {}; team = booking.get("team") or {}
        minute = booking.get("minute") or "—"
        events.append({"minute": str(minute), "player": player.get("name", ""), "assist": "",
                       "team": team.get("name", ""), "type": booking.get("card", "Card"),
                       "detail": "Booking", "is_goal": False})
    for sub in substitutions:
        player_in = sub.get("playerIn") or {}; player_out = sub.get("playerOut") or {}; team = sub.get("team") or {}
        events.append({"minute": str(sub.get("minute") or "—"), "player": player_in.get("name", "Substitution"),
                       "assist": "", "team": team.get("name", ""), "type": "Substitution",
                       "detail": f"On: {player_in.get('name', '—')} · Off: {player_out.get('name', '—')}", "is_goal": False})
    events.sort(key=lambda event: (int(str(event["minute"]).split("+")[0]) if str(event["minute"]).split("+")[0].isdigit() else 999, event["type"]))
    scorers = [event for event in events if event.get("is_goal")]
    detail = {"referee": (snapshot.get("referees") or [])}
    return render(request, "portal/match_detail.html", {
        "match": match, "events": events, "scorers": scorers, "stats": stats, "players": players,
        "detail": detail, "api_error": api_error,
        "has_detail_data": bool(events or snapshot),
    })


def matches_api(request):
    status = request.GET.get("status")
    qs = Match.objects.filter(competition=REAL_COMPETITION).select_related("home_team", "away_team")
    if status in ("FT", "LIVE", "UPCOMING", "POSTPONED"):
        qs = qs.filter(status=status)
    qs = qs.order_by("match_date") if status == "UPCOMING" else qs.order_by("-match_date")
    data = [{"id": m.id, "date": m.match_date.strftime("%d %b %Y, %I:%M %p"), "home": m.home_team.name,
             "away": m.away_team.name, "home_short": m.home_team.short_name, "away_short": m.away_team.short_name,
             "home_crest": m.home_team.crest_url, "away_crest": m.away_team.crest_url,
             "home_score": m.home_score, "away_score": m.away_score, "status": m.status,
             "competition": m.competition, "detail_url": f"/matches/{m.id}/"} for m in qs[:50]]
    return JsonResponse({"matches": data, "source": "football-data.org"})
