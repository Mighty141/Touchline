from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("portal", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="team",
            name="crest_url",
            field=models.URLField(blank=True, default="", max_length=500),
        ),
    ]
