# Generated by Django 2.2.10 on 2020-06-30 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_auto_20200630_2159'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='ref_code',
            field=models.CharField(default='123', max_length=20),
            preserve_default=False,
        ),
    ]