# Generated by Django 2.0.4 on 2018-05-26 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('universityloanoffice', '0002_signingsession'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='status',
            field=models.CharField(choices=[('discontinued', 'discontinued'), ('continuous', 'continuous'), ('postpone', 'postpone'), ('complete', 'complete')], max_length=12),
        ),
    ]
