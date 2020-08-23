# Generated by Django 3.1 on 2020-08-23 11:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('triage', '0001_initial'),
        ('issues', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='main_language',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='triage.programminglanguage'),
        ),
    ]