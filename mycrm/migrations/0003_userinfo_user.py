# Generated by Django 2.0.5 on 2018-08-27 08:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rbacapp', '0002_auto_20180825_1438'),
        ('mycrm', '0002_customerdistribute'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='rbacapp.User'),
        ),
    ]
