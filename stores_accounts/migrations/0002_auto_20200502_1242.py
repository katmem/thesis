# Generated by Django 2.1.5 on 2020-05-02 12:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cities_light', '0008_city_timezone'),
        ('stores_accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='store',
            unique_together={('name', 'phone', 'city', 'address', 'addressNum', 'postcode')},
        ),
    ]
