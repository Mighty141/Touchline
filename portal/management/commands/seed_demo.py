from django.core.management.base import BaseCommand
from portal.models import Team, Player, Match


class Command(BaseCommand):
    help = "Remove fictional demo football records without creating mock teams."

    def handle(self, *args, **kwargs):
        # Keep only imported Premier League matches. This also safely removes
        # old fictional matches left behind by earlier versions of Touchline.
        Match.objects.exclude(competition="Premier League").delete()
        real_team_ids = set(Match.objects.filter(competition="Premier League").values_list("home_team_id", flat=True))
        real_team_ids.update(Match.objects.filter(competition="Premier League").values_list("away_team_id", flat=True))

        Player.objects.exclude(team_id__in=real_team_ids).delete()
        Team.objects.exclude(id__in=real_team_ids).delete()

        if real_team_ids:
            self.stdout.write(self.style.SUCCESS(
                f"Removed fictional demo records. Kept {len(real_team_ids)} teams associated with imported Premier League fixtures."
            ))
            self.stdout.write("Run `python manage.py sync_premier_league` whenever you want to refresh real data.")
        else:
            Player.objects.all().delete()
            Team.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Removed all fictional demo football data. No mock teams were created."))
            self.stdout.write("To populate Touchline, configure FOOTBALL_DATA_ORG_API_KEY and run `python manage.py sync_premier_league`.")
