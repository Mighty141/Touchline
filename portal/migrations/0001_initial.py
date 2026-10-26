# Initial database schema for Touchline.
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="Team",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=80, unique=True)),
                ("short_name", models.CharField(max_length=5)),
                ("color", models.CharField(default="#6c5ce7", max_length=7)),
                ("city", models.CharField(blank=True, max_length=80)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Match",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("match_date", models.DateTimeField()),
                ("home_score", models.PositiveSmallIntegerField(default=0)),
                ("away_score", models.PositiveSmallIntegerField(default=0)),
                ("competition", models.CharField(default="Touchline League", max_length=100)),
                ("status", models.CharField(choices=[("FT", "Full time"), ("UPCOMING", "Upcoming")], default="UPCOMING", max_length=10)),
                ("away_team", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="away_matches", to="portal.team")),
                ("home_team", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="home_matches", to="portal.team")),
            ],
            options={"ordering": ["-match_date"]},
        ),
        migrations.CreateModel(
            name="Player",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("position", models.CharField(max_length=30)),
                ("goals", models.PositiveIntegerField(default=0)),
                ("assists", models.PositiveIntegerField(default=0)),
                ("appearances", models.PositiveIntegerField(default=0)),
                ("team", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="players", to="portal.team")),
            ],
            options={"ordering": ["-goals", "name"]},
        ),
    ]
