# Generated by Django 4.2.6 on 2023-10-24 09:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_alter_chatroommembership_chat_room'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chatroommembership',
            old_name='username',
            new_name='user',
        ),
    ]
