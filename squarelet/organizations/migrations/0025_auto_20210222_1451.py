# Generated by Django 2.1.7 on 2021-02-22 19:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0024_auto_20200623_0950'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrganizationSubtype',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='The name of the organization subtype', max_length=255, verbose_name='name')),
            ],
        ),
        migrations.CreateModel(
            name='OrganizationType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='The name of the organization type', max_length=255, verbose_name='name')),
            ],
        ),
        migrations.AddField(
            model_name='organizationsubtype',
            name='type',
            field=models.ForeignKey(help_text='The parent type for this subtype', on_delete=django.db.models.deletion.PROTECT, related_name='subtypes', to='organizations.OrganizationType', verbose_name='type'),
        ),
        migrations.AddField(
            model_name='organization',
            name='subtypes',
            field=models.ManyToManyField(help_text='The subtypes of this organization', related_name='organizations', to='organizations.OrganizationSubtype', verbose_name='subtypes'),
        ),
    ]