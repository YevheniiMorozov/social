# Generated by Django 4.0.5 on 2022-07-14 22:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialnet', '0009_alter_account_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='username',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
