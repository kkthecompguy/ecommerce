# Generated by Django 2.2.8 on 2020-03-24 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20200324_1511'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='category',
            field=models.CharField(choices=[('S', 'Mens Shirt'), ('WA', 'Women Dress'), ('SW', 'Sport wear'), ('OW', 'Outwear'), ('E', 'Electronics'), ('C', 'Computing devices'), ('N', 'Network devices'), ('F', 'Furniture'), ('FB', 'Food and Beverages'), ('U', 'Utensils'), ('P', 'Phones'), ('SH', 'Shoes'), ('BB', 'Baby Care')], max_length=2),
        ),
    ]
