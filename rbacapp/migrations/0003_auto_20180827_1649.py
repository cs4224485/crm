# Generated by Django 2.0.5 on 2018-08-27 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rbacapp', '0002_auto_20180825_1438'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permission',
            name='url',
            field=models.CharField(max_length=128),
        ),
    ]