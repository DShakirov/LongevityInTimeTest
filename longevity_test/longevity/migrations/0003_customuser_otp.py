# Generated by Django 4.2.4 on 2023-08-30 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('longevity', '0002_customuser_about_me'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='otp',
            field=models.CharField(default='Aa11111', max_length=6),
            preserve_default=False,
        ),
    ]
