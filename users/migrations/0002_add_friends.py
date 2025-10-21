from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='friends',
            field=models.ManyToManyField(related_name='friends_rel', to=settings.AUTH_USER_MODEL, blank=True, help_text='Users you are friends with'),
        ),
    ]
