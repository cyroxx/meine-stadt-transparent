# Generated by Django 2.1.8 on 2019-04-05 07:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0022_auto_20190404_1605'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalpaper',
            name='reference_number',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='paper',
            name='reference_number',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]