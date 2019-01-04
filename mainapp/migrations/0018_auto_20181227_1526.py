# Generated by Django 2.1.4 on 2018-12-27 14:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0017_merge_20181221_1508'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='searchpoi',
            name='bodies',
        ),
        migrations.RemoveField(
            model_name='searchstreet',
            name='bodies',
        ),
        migrations.AddField(
            model_name='historicalsearchpoi',
            name='body',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='mainapp.Body'),
        ),
        migrations.AddField(
            model_name='historicalsearchstreet',
            name='body',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='mainapp.Body'),
        ),
        migrations.AddField(
            model_name='searchpoi',
            name='body',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mainapp.Body'),
        ),
        migrations.AddField(
            model_name='searchstreet',
            name='body',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mainapp.Body'),
        ),
    ]