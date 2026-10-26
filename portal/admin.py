from django.contrib import admin
from .models import Team, Player, Match
@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name","short_name","city")
    search_fields = ("name","short_name")
@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("name","team","position","goals","assists")
    list_filter = ("team","position")
    search_fields = ("name",)
@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ("match_date","home_team","home_score","away_score","away_team","status")
    list_filter = ("status","competition")
