# Generated by Django 2.0.6 on 2019-02-13 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_user_use_autologin'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='source',
            field=models.CharField(choices=[('muckrock', 'MuckRock'), ('documentcloud', 'DocumentCloud'), ('foiamachine', 'FOIA Machine'), ('quackbot', 'QuackBot'), ('squarelet', 'Squarelet')], default='squarelet', max_length=11),
        ),
    ]