# Generated by Django 2.1.7 on 2020-04-07 15:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0016_auto_20200113_1638'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='entitlement',
            options={'ordering': ('slug',)},
        ),
        migrations.AlterModelOptions(
            name='membership',
            options={'ordering': ('user_id',)},
        ),
        migrations.AlterModelOptions(
            name='plan',
            options={'ordering': ('slug',)},
        ),
        migrations.AlterModelOptions(
            name='subscription',
            options={'ordering': ('plan',)},
        ),
    ]
