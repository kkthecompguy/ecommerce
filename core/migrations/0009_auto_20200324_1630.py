# Generated by Django 2.2.8 on 2020-03-24 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20200324_1601'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='additional_info',
            field=models.TextField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='description',
            field=models.TextField(blank=True, max_length=1000, null=True),
        ),
    ]
