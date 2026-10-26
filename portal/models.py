from django.db import models


class Team(models.Model):
    name = models.CharField(max_length=120, unique=True)
    short_name = models.CharField(max_length=12, blank=True)
    color = models.CharField(max_length=7, default="#6c5ce7")
    crest_url = models.URLField(max_length=700, blank=True, default="")
    city = models.CharField(max_length=100, blank=True)
    api_id = models.CharField(max_length=80, unique=True, null=True, blank=True)
    table_position = models.PositiveSmallIntegerField(default=0)
    played = models.PositiveSmallIntegerField(default=0)
    wins = models.PositiveSmallIntegerField(default=0)
    draws = models.PositiveSmallIntegerField(default=0)
    losses = models.PositiveSmallIntegerField(default=0)
    goals_for = models.PositiveSmallIntegerField(default=0)
    goals_against = models.PositiveSmallIntegerField(default=0)
    points = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["table_position", "name"]

    @property
    def goal_difference(self):
        return self.goals_for - self.goals_against

    def __str__(self):
        return self.name


class Player(models.Model):
    name = models.CharField(max_length=120)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="players")
    position = models.CharField(max_length=40, blank=True, default="Player")
    goals = models.PositiveIntegerField(default=0)
    assists = models.PositiveIntegerField(default=0)
    appearances = models.PositiveIntegerField(default=0)
    api_id = models.CharField(max_length=80, null=True, blank=True)

    class Meta:
        ordering = ["-goals", "name"]

    def __str__(self):
        return f"{self.name} ({self.team.short_name})"


class Match(models.Model):
    STATUS_CHOICES = [("FT", "Full time"), ("LIVE", "Live"), ("UPCOMING", "Upcoming"), ("POSTPONED", "Postponed")]
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="home_matches")
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="away_matches")
    match_date = models.DateTimeField()
    home_score = models.PositiveSmallIntegerField(default=0)
    away_score = models.PositiveSmallIntegerField(default=0)
    competition = models.CharField(max_length=100, default="Premier League")
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="UPCOMING")
    api_match_id = models.CharField(max_length=80, unique=True, null=True, blank=True)
    venue = models.CharField(max_length=160, blank=True, default="")
    matchweek = models.CharField(max_length=30, blank=True, default="")
    round_name = models.CharField(max_length=100, blank=True, default="")
    halftime_home_score = models.PositiveSmallIntegerField(null=True, blank=True)
    halftime_away_score = models.PositiveSmallIntegerField(null=True, blank=True)
    detail_snapshot = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-match_date"]

    def __str__(self):
        return f"{self.home_team.short_name} vs {self.away_team.short_name}"
