# Generated by Django 2.0.4 on 2018-05-04 23:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aris', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='college',
            name='college_name',
            field=models.CharField(max_length=100, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='degree',
            name='programe_name',
            field=models.CharField(max_length=100, primary_key=True, serialize=False),
        ),
    ]
