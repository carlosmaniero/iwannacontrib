# Generated by Django 3.1 on 2020-08-23 13:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('issues', '0004_auto_20200823_1319'),
    ]

    operations = [
        migrations.RenameField(
            model_name='issueraterel',
            old_name='icon',
            new_name='rate',
        ),
    ]