# Generated by Django 3.1 on 2020-08-20 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20200820_0343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='musician',
            name='headshot',
            field=models.ImageField(blank=True, null=True, upload_to='images/'),
        ),
    ]