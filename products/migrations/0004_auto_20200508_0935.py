# Generated by Django 2.1.5 on 2020-05-08 09:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_auto_20200508_0832'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredients',
            name='slug',
            field=models.SlugField(blank=True, max_length=20, unique=True),
        ),
    ]
