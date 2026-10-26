from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("portal", "0002_team_crest_url")]
    operations = [
        migrations.AddField(model_name="team", name="api_id", field=models.CharField(blank=True, max_length=80, null=True, unique=True)),
        migrations.AddField(model_name="team", name="table_position", field=models.PositiveSmallIntegerField(default=0)),
        migrations.AddField(model_name="team", name="played", field=models.PositiveSmallIntegerField(default=0)),
        migrations.AddField(model_name="team", name="wins", field=models.PositiveSmallIntegerField(default=0)),
        migrations.AddField(model_name="team", name="draws", field=models.PositiveSmallIntegerField(default=0)),
        migrations.AddField(model_name="team", name="losses", field=models.PositiveSmallIntegerField(default=0)),
        migrations.AddField(model_name="team", name="goals_for", field=models.PositiveSmallIntegerField(default=0)),
        migrations.AddField(model_name="team", name="goals_against", field=models.PositiveSmallIntegerField(default=0)),
        migrations.AddField(model_name="team", name="points", field=models.PositiveSmallIntegerField(default=0)),
        migrations.AlterField(model_name="team", name="name", field=models.CharField(max_length=120, unique=True)),
        migrations.AlterField(model_name="team", name="short_name", field=models.CharField(blank=True, max_length=12)),
        migrations.AlterField(model_name="team", name="crest_url", field=models.URLField(blank=True, default="", max_length=700)),
        migrations.AlterField(model_name="team", name="city", field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name="player", name="api_id", field=models.CharField(blank=True, max_length=80, null=True)),
        migrations.AlterField(model_name="player", name="name", field=models.CharField(max_length=120)),
        migrations.AlterField(model_name="player", name="position", field=models.CharField(blank=True, default="Player", max_length=40)),
        migrations.AlterField(model_name="match", name="status", field=models.CharField(choices=[("FT", "Full time"), ("LIVE", "Live"), ("UPCOMING", "Upcoming"), ("POSTPONED", "Postponed")], default="UPCOMING", max_length=12)),
        migrations.AddField(model_name="match", name="api_match_id", field=models.CharField(blank=True, max_length=80, null=True, unique=True)),
        migrations.AddField(model_name="match", name="venue", field=models.CharField(blank=True, default="", max_length=160)),
        migrations.AddField(model_name="match", name="matchweek", field=models.CharField(blank=True, default="", max_length=30)),
        migrations.AddField(model_name="match", name="round_name", field=models.CharField(blank=True, default="", max_length=100)),
        migrations.AddField(model_name="match", name="halftime_home_score", field=models.PositiveSmallIntegerField(blank=True, null=True)),
        migrations.AddField(model_name="match", name="halftime_away_score", field=models.PositiveSmallIntegerField(blank=True, null=True)),
        migrations.AddField(model_name="match", name="detail_snapshot", field=models.JSONField(blank=True, default=dict)),
    ]
