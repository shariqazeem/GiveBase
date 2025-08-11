# In your_app/migrations/XXXX_add_points_system.py

from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0004_remove_donation_points_earned_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='pooldonation',
            name='points_earned',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='socialdonation',
            name='points_earned',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='total_points',
            field=models.BigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='donation',
            name='points_earned',
            field=models.BigIntegerField(default=0),
        ),
    ]