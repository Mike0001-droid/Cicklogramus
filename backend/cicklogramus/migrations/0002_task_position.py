# Generated manually for adding position field to Task model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cicklogramus', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='position',
            field=models.IntegerField(default=0, verbose_name='Позиция в списке'),
        ),
    ]
