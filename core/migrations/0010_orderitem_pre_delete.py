# Generated by Django 2.2.10 on 2020-06-27 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20200626_1752'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='pre_delete',
            field=models.BooleanField(default=False),
        ),
    ]
