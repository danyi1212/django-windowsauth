# Generated by Django 3.1.4 on 2020-12-05 20:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LDAPUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.CharField(help_text='User Domain NetBIOS Name', max_length=128)),
                ('last_sync', models.DateTimeField(help_text='Last time performed LDAP sync for user attributes and group membership')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='ldap', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
