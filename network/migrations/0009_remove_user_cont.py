# Generated by Django 4.1.4 on 2023-01-30 13:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0008_alter_user_follows'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='cont',
        ),
    ]
